"""
D2. BinanceWebSocketFeed: REST polling → WebSocket 실시간 캔들 피드.

Binance 공개 WebSocket (인증 불필요):
  wss://stream.binance.com:9443/ws/{symbol}@kline_{interval}

설계:
  - 백그라운드 스레드에서 asyncio 루프 실행
  - 완성된 캔들(is_closed=True)만 버퍼에 추가
  - DataFeed와 동일한 인터페이스: get_latest_df() → pd.DataFrame
  - 연결 끊김 시 자동 재연결 (exponential backoff + jitter, 최대 5회)
  - OrderBook Imbalance: bid/ask 압력 실시간 추적
  - websockets 패키지 없으면 REST fallback 자동 전환
  - 연결 상태 메트릭: last_candle_ts, reconnection_count, uptime

사용:
  feed = BinanceWebSocketFeed("btcusdt", "1h")
  feed.start()
  df = feed.get_latest_df(limit=500)  # DataFeed.fetch()와 동일 반환
  metrics = feed.get_connection_metrics()  # 연결 상태 조회
  feed.stop()
"""

import asyncio
import json
import logging
import threading
import time
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, Deque, Dict, Any, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"
MAX_CANDLES = 1000      # 보유 최대 캔들 수
MAX_RETRY = 5
RETRY_BASE = 2.0        # 재연결 대기 기본 (초)
RETRY_JITTER = 0.1      # 지터 계수 (0~10%의 랜덤 지연 추가)
MAX_BACKOFF = 60.0      # 최대 백오프 (초) — 지수 증가 상한


@dataclass
class CandleBar:
    """완성된 캔들 1개."""
    timestamp: int   # ms
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class OrderBookImbalance:
    """호가 불균형 신호."""
    bid_volume: float
    ask_volume: float
    imbalance: float    # (bid-ask)/(bid+ask), -1~+1
    pressure: str       # "BUY_PRESSURE" | "SELL_PRESSURE" | "NEUTRAL"


@dataclass
class ConnectionMetrics:
    """WebSocket 연결 상태 메트릭."""
    is_connected: bool
    retry_count: int
    last_candle_timestamp: Optional[float] = None
    reconnection_count: int = 0
    uptime_seconds: Optional[float] = None
    total_candles_received: int = 0
    consecutive_failures: int = 0


class ConnectionHealthMonitor:
    """연결 상태 장기 추적 모니터."""

    _MAX_HISTORY = 10

    def __init__(self) -> None:
        self._start_time: float = time.time()
        self._last_candle_time: Optional[float] = None
        self._reconnection_history: deque = deque(maxlen=self._MAX_HISTORY)

    def record_reconnection(self, reason: str) -> None:
        """재연결 이벤트 기록."""
        self._reconnection_history.append({"timestamp": time.time(), "reason": reason})

    def record_candle(self) -> None:
        """캔들 수신 시 마지막 수신 시간 갱신."""
        self._last_candle_time = time.time()

    def is_stale(self, timeout_seconds: float = 300.0) -> bool:
        """마지막 캔들 수신 후 timeout_seconds 초 이상 경과하면 True.
        캔들을 한 번도 수신하지 않은 경우 False 반환 (아직 초기화 중).
        """
        if self._last_candle_time is None:
            return False
        return (time.time() - self._last_candle_time) >= timeout_seconds

    def reconnection_rate(self, window_seconds: float = 3600.0) -> float:
        """최근 window_seconds 내 재연결 횟수 반환. 비율 높으면 연결 불안정."""
        now = time.time()
        cutoff = now - window_seconds
        return sum(1 for ev in self._reconnection_history if ev["timestamp"] >= cutoff)

    def is_flapping(self, window_seconds: float = 300.0, threshold: int = 3) -> bool:
        """5분 내 재연결이 threshold 이상이면 flapping(불안정) 판정."""
        return self.reconnection_rate(window_seconds) >= threshold


    def validate_timeout_setting(self, base_interval: float, stale_timeout: float) -> dict:
        """
        타임아웃 설정 검증 및 조정 (Cycle 229).
        
        Args:
            base_interval: 타임프레임 기간 (초, 예: 1h=3600s)
            stale_timeout: 현재 설정된 stale timeout (초)
        
        Returns:
            dict with validation results:
            {
                'is_valid': bool,               # 타임아웃이 합리적인 범위인지
                'recommended_timeout': float,   # 권장 타임아웃 (base_interval * 1.5)
                'current_timeout': float,       # 현재 설정값
                'warning': str or None,         # 경고 메시지 (문제시)
                'suggestion': str or None,      # 개선 제안 (문제시)
            }
        
        Notes:
            - 타임아웃 < base_interval: 정상 캔들도 stale 판정 위험
            - 타임아웃 > base_interval * 5: 장시간 지연 감지 불가
            - 권장: base_interval * 1.5 (50% 여유)
        """
        recommended = base_interval * 1.5
        is_valid = True
        warning = None
        suggestion = None
        
        if stale_timeout < base_interval:
            is_valid = False
            warning = f"Timeout {stale_timeout}s < base_interval {base_interval}s: may incorrectly flag normal candles as stale"
            suggestion = f"Increase timeout to at least {base_interval * 1.5}s"
        elif stale_timeout > base_interval * 5:
            warning = f"Timeout {stale_timeout}s > base_interval*5 ({base_interval*5}s): may miss connection issues"
            suggestion = f"Consider {recommended}s for faster stale detection"
        
        return {
            'is_valid': is_valid,
            'recommended_timeout': recommended,
            'current_timeout': stale_timeout,
            'warning': warning,
            'suggestion': suggestion,
        }

    def get_health_summary(self) -> dict:
        """연결 상태 요약 딕셔너리 반환."""
        now = time.time()
        last_candle_age = (now - self._last_candle_time) if self._last_candle_time is not None else None
        return {
            "uptime_seconds": now - self._start_time,
            "total_reconnections": len(self._reconnection_history),
            "last_candle_age_seconds": last_candle_age,
            "is_healthy": not self.is_stale() and not self.is_flapping(),
            "is_flapping": self.is_flapping(),
            "reconnection_rate_1h": self.reconnection_rate(3600.0),
            "reconnection_history": list(self._reconnection_history),
        }


class BinanceWebSocketFeed:
    """
    Binance WebSocket 기반 실시간 캔들 피드.

    websockets 패키지 필요: pip install websockets
    없으면 is_websocket_available() = False, REST fallback 권장.
    
    Reconnection 전략:
    - exponential backoff: 2^retry_count (초)
    - jitter: ±10% 랜덤 지연 추가 (thundering herd 방지)
    - max_retry: 5회 (약 62초 누적)
    """

    def __init__(self, symbol: str = "btcusdt", interval: str = "1h", stale_timeout: Optional[float] = None):
        self.symbol = symbol.lower().replace("/", "")
        self.interval = interval
        # Cycle 229: 타임프레임 기반 동적 타임아웃 계산
        # 타임프레임별 기대 캔들 수신 간격: 1h=3600s, 4h=14400s, 1d=86400s
        # 타임아웃 = 캔들 간격 * 1.5 (50% 여유)
        tf_intervals = {
            "1m": 60, "5m": 300, "15m": 900,
            "1h": 3600, "4h": 14400, "1d": 86400
        }
        base_interval = tf_intervals.get(interval, 3600)
        # None이면 타임프레임 기반 동적 계산, 명시적 값(0 포함)이면 그대로 사용
        if stale_timeout is not None:
            self._stale_timeout = stale_timeout  # 명시적 설정값 사용 (0도 유효)
        else:
            self._stale_timeout = base_interval * 1.5  # 동적 계산 (타임프레임 * 1.5)
        self._base_interval = base_interval  # 타임프레임 기간 저장 (나중에 재조정용)
        self._candles: Deque[CandleBar] = deque(maxlen=MAX_CANDLES)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connected = False
        self._last_obi: Optional[OrderBookImbalance] = None
        self._retry_count = 0
        self._last_candle_timestamp_ms: Optional[int] = None  # 중복 캔들 방지

        # Health monitor
        self._health_monitor = ConnectionHealthMonitor()

        # Metrics tracking
        self._start_time: Optional[float] = None
        self._last_candle_ts: Optional[float] = None
        self._reconnection_count = 0
        self._total_candles_received = 0
        self._consecutive_failures = 0

        # Reconnect gap tracking (Cycle 239)
        self._reconnect_gaps: Deque[Dict[str, Any]] = deque(maxlen=100)
        self._last_recv_ts: Optional[float] = None  # 마지막 데이터 수신 시각 (wall clock)
        self._pending_gap_start: Optional[float] = None  # reconnect 시 갭 시작 시점

    @staticmethod
    def is_websocket_available() -> bool:
        try:
            import websockets  # noqa
            return True
        except ImportError:
            return False

    def start(self) -> bool:
        """WebSocket 수신 시작. websockets 없으면 False 반환."""
        if not self.is_websocket_available():
            logger.warning("websockets 패키지 없음 (pip install websockets) → REST 사용 권장")
            return False

        self._stop_event.clear()
        self._start_time = time.time()
        self._reconnection_count = 0
        self._consecutive_failures = 0
        self._thread = threading.Thread(
            target=self._run_loop,
            name=f"ws-{self.symbol}-{self.interval}",
            daemon=True,
        )
        self._thread.start()
        logger.info("WebSocketFeed started: %s@kline_%s", self.symbol, self.interval)
        return True

    def stop(self) -> None:
        """WebSocket 수신 중지."""
        self._stop_event.set()
        # Guard against race condition: if stop() is called before _run_loop()
        # assigns self._loop, _loop will be None. The _stop_event.set() above
        # ensures clean exit via _stop_event.is_set() check in _connect_with_retry.
        if self._loop is not None and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("WebSocketFeed stopped")

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_latest_df(self, limit: int = 500) -> Optional[pd.DataFrame]:
        """
        최근 limit개 완성 캔들 → DataFrame (DataFeed.fetch()와 호환).
        캔들이 없으면 None 반환.
        """
        with self._lock:
            bars = list(self._candles)[-limit:]

        if not bars:
            return None

        df = pd.DataFrame(
            [
                {
                    "timestamp": b.timestamp,
                    "open": b.open,
                    "high": b.high,
                    "low": b.low,
                    "close": b.close,
                    "volume": b.volume,
                }
                for b in bars
            ]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        df = self._add_indicators(df)
        return df

    def get_order_book_imbalance(self) -> Optional[OrderBookImbalance]:
        """최신 호가 불균형 반환."""
        return self._last_obi

    def candle_count(self) -> int:
        return len(self._candles)

    def get_health_summary(self) -> dict:
        """연결 상태 장기 요약 반환 (ConnectionHealthMonitor 위임)."""
        return self._health_monitor.get_health_summary()

    def get_connection_metrics(self) -> ConnectionMetrics:
        """
        현재 연결 상태 및 성능 메트릭 반환.
        
        Returns:
            ConnectionMetrics: 연결 상태, 재시도 횟수, 수신 통계
        """
        uptime = None
        if self._start_time is not None:
            uptime = time.time() - self._start_time
        
        return ConnectionMetrics(
            is_connected=self._connected,
            retry_count=self._retry_count,
            last_candle_timestamp=self._last_candle_ts,
            reconnection_count=self._reconnection_count,
            uptime_seconds=uptime,
            total_candles_received=self._total_candles_received,
            consecutive_failures=self._consecutive_failures,
        )

    def get_reconnect_gaps(self) -> List[Dict[str, Any]]:
        """
        Reconnect 발생 시 기록된 데이터 갭 목록 반환 (Cycle 239).

        각 reconnect 이벤트에서 마지막 수신 타임스탬프와 재연결 후 첫 수신
        타임스탬프 사이의 갭을 계산하여 기록한다.

        Returns:
            List[dict]: 각 dict는 {"start": float, "end": float, "gap_seconds": float}
                        start/end는 UNIX epoch (time.time()) 기준.
            최대 100개까지 보관 (FIFO).
        """
        return list(self._reconnect_gaps)

    def _record_reconnect_gap(self, gap_start: float, gap_end: float) -> None:
        """reconnect 갭 기록 (내부용)."""
        gap_seconds = gap_end - gap_start
        self._reconnect_gaps.append({
            "start": gap_start,
            "end": gap_end,
            "gap_seconds": gap_seconds,
        })
        logger.info(
            "Reconnect gap recorded: %.1fs (start=%.1f, end=%.1f)",
            gap_seconds, gap_start, gap_end,
        )

    def validate_timeout_config(self) -> dict:
        """
        현재 타임아웃 설정 검증 (Cycle 229).
        
        Returns:
            타임아웃 검증 결과 (validate_timeout_setting 위임)
        """
        return self._health_monitor.validate_timeout_setting(
            base_interval=self._base_interval,
            stale_timeout=self._stale_timeout,
        )

    # ------------------------------------------------------------------
    # Async WebSocket loop (백그라운드 스레드)
    # ------------------------------------------------------------------

    def _run_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connect_with_retry())
        except Exception as e:
            logger.error("WebSocket loop error: %s", e)
        finally:
            self._loop.close()

    def _calculate_backoff_with_jitter(self, retry_count: int) -> float:
        """
        지수 백오프 + 지터 계산 (MAX_BACKOFF 상한 적용).

        공식: backoff = min(base^retry_count, MAX_BACKOFF) * (1 + jitter * random_factor)
        예: base=2, jitter=0.1, max=60
          - retry=1: 2 * (1 ± 0.1) = 1.8 ~ 2.2초
          - retry=2: 4 * (1 ± 0.1) = 3.6 ~ 4.4초
          - retry=5: 32 * (1 ± 0.1) = 28.8 ~ 35.2초
          - retry=7: min(128, 60) * (1 ± 0.1) = 54 ~ 66초
        """
        base_delay = min(RETRY_BASE ** retry_count, MAX_BACKOFF)
        jitter_factor = 1.0 + (random.random() * 2 - 1) * RETRY_JITTER
        return base_delay * jitter_factor

    async def _connect_with_retry(self) -> None:
        while not self._stop_event.is_set() and self._retry_count < MAX_RETRY:
            try:
                await self._listen()
                self._retry_count = 0  # 성공 시 리셋
                self._consecutive_failures = 0
            except Exception as e:
                self._connected = False
                self._retry_count += 1
                self._consecutive_failures += 1
                self._health_monitor.record_reconnection(reason=str(e))

                # Reconnect gap tracking: 이전에 데이터를 수신한 적이 있으면
                # 갭 시작 시점 기록 → 다음 캔들 수신 시 갭 완결
                if self._last_recv_ts is not None:
                    self._pending_gap_start = self._last_recv_ts

                wait = self._calculate_backoff_with_jitter(self._retry_count)
                logger.warning(
                    "WebSocket disconnected (retry %d/%d in %.2fs): %s",
                    self._retry_count, MAX_RETRY, wait, e,
                )
                
                if self._retry_count < MAX_RETRY:
                    await asyncio.sleep(wait)

        if self._retry_count >= MAX_RETRY:
            logger.error("WebSocket max retries exceeded — feed stopped")
            self._consecutive_failures = MAX_RETRY

    async def _message_loop(self, ws) -> None:
        """WebSocket 메시지 수신 루프."""
        async for msg in ws:
            if self._stop_event.is_set():
                return
            try:
                self._process_message(json.loads(msg))
            except Exception as e:
                logger.debug("Message parse error: %s", e)

    async def _stale_watchdog(self) -> None:
        """캔들 stale 감지 → 예외 발생으로 재연결 트리거."""
        while not self._stop_event.is_set():
            await asyncio.sleep(30.0)
            if self._health_monitor.is_stale(timeout_seconds=self._stale_timeout):
                logger.warning(
                    "Stale connection detected (no candle for >%.0fs) — forcing reconnect",
                    self._stale_timeout,
                )
                raise ConnectionError(f"Stale: no candle for >{self._stale_timeout}s")

    async def _listen(self) -> None:
        import websockets

        url = f"{BINANCE_WS_BASE}/{self.symbol}@kline_{self.interval}"
        logger.info("Connecting to %s", url)

        try:
            async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                self._connected = True
                self._reconnection_count += 1
                self._health_monitor.record_reconnection(reason="connect")
                logger.info("WebSocket connected: %s (reconnection #%d)", url, self._reconnection_count)

                tasks = [
                    asyncio.create_task(self._message_loop(ws)),
                    asyncio.create_task(self._stale_watchdog()),
                ]
                try:
                    done, pending = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_EXCEPTION
                    )
                    for t in pending:
                        t.cancel()
                    for t in done:
                        exc = t.exception()
                        if exc:
                            raise exc
                except Exception:
                    for t in tasks:
                        t.cancel()
                    raise
        finally:
            self._connected = False

    def _process_message(self, data: dict) -> None:
        """kline 메시지 파싱 → 완성 캔들 저장."""
        k = data.get("k", {})
        if not k:
            return

        is_closed = k.get("x", False)
        if not is_closed:
            return  # 미완성 캔들 무시

        ts_ms = int(k["t"])
        # 재연결 시 동일 타임스탬프 중복 캔들 방지
        if self._last_candle_timestamp_ms is not None and ts_ms <= self._last_candle_timestamp_ms:
            logger.debug("Duplicate candle skipped: ts=%d (last=%d)", ts_ms, self._last_candle_timestamp_ms)
            return

        bar = CandleBar(
            timestamp=ts_ms,
            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"]),
            volume=float(k["v"]),
        )
        now = time.time()
        with self._lock:
            self._candles.append(bar)
            self._last_candle_timestamp_ms = ts_ms
            self._last_candle_ts = now
            self._total_candles_received += 1

            # Reconnect gap detection: 이전 수신 이력이 있고 reconnect 직후
            # 첫 캔들이면 갭 기록 (_pending_gap_start가 설정된 상태)
            if getattr(self, "_pending_gap_start", None) is not None:
                self._record_reconnect_gap(self._pending_gap_start, now)
                self._pending_gap_start = None
            self._last_recv_ts = now
        self._health_monitor.record_candle()

        logger.debug(
            "New candle: %s O=%.2f H=%.2f L=%.2f C=%.2f V=%.2f",
            pd.Timestamp(bar.timestamp, unit="ms"),
            bar.open, bar.high, bar.low, bar.close, bar.volume,
        )

    # ------------------------------------------------------------------
    # Indicators (DataFeed._add_indicators와 동일)
    # ------------------------------------------------------------------

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        high = df["high"]
        low = df["low"]

        df["ema20"] = close.ewm(span=20, adjust=False).mean()
        df["ema50"] = close.ewm(span=50, adjust=False).mean()

        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

        delta = close.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

        df["donchian_high"] = high.rolling(20).max()
        df["donchian_low"] = low.rolling(20).min()

        typical = (high + low + close) / 3
        df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()

        return df


class WebSocketDataAdapter:
    """
    BinanceWebSocketFeed를 DataFeed 인터페이스로 래핑.

    DataFeed.fetch() 대신 WebSocket 캔들 사용.
    캔들 부족 시 REST fallback으로 자동 전환.
    """

    def __init__(
        self,
        ws_feed: BinanceWebSocketFeed,
        rest_feed=None,  # DataFeed (fallback)
        min_candles: int = 100,
    ):
        self._ws = ws_feed
        self._rest = rest_feed
        self._min_candles = min_candles

    def fetch(self, symbol: str, timeframe: str, limit: int = 500):
        """DataFeed.fetch()와 동일 인터페이스."""
        if self._ws.is_connected and self._ws.candle_count() >= self._min_candles:
            df = self._ws.get_latest_df(limit=limit)
            if df is not None:
                from src.data.feed import DataSummary
                return DataSummary(
                    symbol=symbol,
                    timeframe=timeframe,
                    candles=len(df),
                    start=str(df.index[0]),
                    end=str(df.index[-1]),
                    missing=0,
                    indicators=[c for c in df.columns if c not in {"open", "high", "low", "close", "volume"}],
                    anomalies=[],
                    df=df,
                )

        # Fallback to REST
        if self._rest:
            logger.debug("WebSocket fallback → REST")
            return self._rest.fetch(symbol, timeframe, limit)

        raise RuntimeError("WebSocket 미연결 + REST fallback 없음")
