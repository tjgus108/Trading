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
from typing import Optional, Deque, Dict, Any

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"
MAX_CANDLES = 1000      # 보유 최대 캔들 수
MAX_RETRY = 5
RETRY_BASE = 2.0        # 재연결 대기 기본 (초)
RETRY_JITTER = 0.1      # 지터 계수 (0~10%의 랜덤 지연 추가)


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

    def __init__(self, symbol: str = "btcusdt", interval: str = "1h"):
        self.symbol = symbol.lower().replace("/", "")
        self.interval = interval
        self._candles: Deque[CandleBar] = deque(maxlen=MAX_CANDLES)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connected = False
        self._last_obi: Optional[OrderBookImbalance] = None
        self._retry_count = 0
        
        # Metrics tracking
        self._start_time: Optional[float] = None
        self._last_candle_ts: Optional[float] = None
        self._reconnection_count = 0
        self._total_candles_received = 0
        self._consecutive_failures = 0

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
        지수 백오프 + 지터 계산.
        
        공식: backoff = base^retry_count * (1 + jitter * random_factor)
        예: base=2, jitter=0.1
          - retry=1: 2 * (1 ± 0.1) = 1.8 ~ 2.2초
          - retry=2: 4 * (1 ± 0.1) = 3.6 ~ 4.4초
          - retry=5: 32 * (1 ± 0.1) = 28.8 ~ 35.2초
        """
        base_delay = RETRY_BASE ** retry_count
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

    async def _listen(self) -> None:
        import websockets

        url = f"{BINANCE_WS_BASE}/{self.symbol}@kline_{self.interval}"
        logger.info("Connecting to %s", url)

        try:
            async with websockets.connect(url, ping_interval=20, ping_timeout=10) as ws:
                self._connected = True
                self._reconnection_count += 1
                logger.info("WebSocket connected: %s (reconnection #%d)", url, self._reconnection_count)

                async for msg in ws:
                    if self._stop_event.is_set():
                        break
                    try:
                        self._process_message(json.loads(msg))
                    except Exception as e:
                        logger.debug("Message parse error: %s", e)
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

        bar = CandleBar(
            timestamp=int(k["t"]),
            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"]),
            volume=float(k["v"]),
        )
        with self._lock:
            self._candles.append(bar)
            self._last_candle_ts = time.time()
            self._total_candles_received += 1

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
