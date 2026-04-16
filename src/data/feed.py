"""
DataFeed: OHLCV 수집 + 기술 지표 계산.
data-agent가 이 모듈을 사용한다.
"""
from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

try:
    import ccxt
except ImportError:
    ccxt = None  # type: ignore[assignment]
import numpy as np
import pandas as pd

from src.exchange.connector import ExchangeConnector
from typing import Dict, List

logger = logging.getLogger(__name__)


# Error classification
def _is_transient_error(error: Exception) -> bool:
    """네트워크/속도 제한 에러는 재시도 가능."""
    transient_types = (
        ccxt.NetworkError,
        ccxt.RequestTimeout,
        ccxt.RateLimitExceeded,
        TimeoutError,
        ConnectionError,
    )
    return isinstance(error, transient_types)


def _is_fatal_error(error: Exception) -> bool:
    """인증, 심볼, 권한 에러는 즉시 중단."""
    fatal_types = (
        ccxt.BadSymbol,
        ccxt.InvalidAddress,
        ccxt.AuthenticationError,
        ccxt.PermissionDenied,
        ValueError,  # Invalid data format
        KeyError,    # Missing required fields
    )
    return isinstance(error, fatal_types)


def _is_rate_limit_error(error: Exception) -> bool:
    """Rate limit 에러 여부 감지."""
    return isinstance(error, ccxt.RateLimitExceeded)


def _backoff_with_rate_limit(error: Exception, attempt: int) -> None:
    """
    Rate limit 에러는 긴 backoff, 다른 transient 에러는 짧은 backoff.
    
    Args:
        error: 발생한 예외
        attempt: 시도 번호 (1부터)
    """
    if _is_rate_limit_error(error):
        # Rate limit: 2초 + attempt * 2초 (2s, 4s, 6s, ...)
        wait_time = 2 + attempt * 2
        logger.info(
            "RateLimitExceeded detected: backing off %d seconds (attempt %d)",
            wait_time, attempt
        )
    else:
        # 다른 transient 에러: 0.5초 * attempt (0.5s, 1s, 1.5s, ...)
        wait_time = 0.5 * attempt
    
    time.sleep(wait_time)



@dataclass
class DataSummary:
    symbol: str
    timeframe: str
    candles: int
    start: str
    end: str
    missing: int
    indicators: List[str]
    anomalies: List[str]
    df: pd.DataFrame = field(repr=False)


class DataFeed:
    def __init__(self, connector: ExchangeConnector, cache_ttl: int = 60, max_retries: int = 3, max_cache_size: int = 128):
        self.connector = connector
        self._cache: dict = {}       # (symbol, timeframe, limit) → (DataSummary, timestamp)
        self._cache_ttl = cache_ttl  # 초
        self._max_cache_size = max_cache_size  # 최대 캐시 엔트리 수
        self._max_retries = max_retries
        self._hit_count = 0          # 캐시 히트 수
        self._miss_count = 0         # 캐시 미스 수

    def fetch(self, symbol: str, timeframe: str, limit: int = 500) -> DataSummary:
        key = (symbol, timeframe, limit)
        now = time.time()
        if key in self._cache:
            cached_summary, ts = self._cache[key]
            if now - ts < self._cache_ttl:
                self._hit_count += 1
                return cached_summary  # 캐시 히트
        # 캐시 미스: 실제 fetch (retry 포함)
        self._miss_count += 1
        summary = self._fetch_with_retry(symbol, timeframe, limit)
        self._cache[key] = (summary, now)
        self._evict_if_needed()
        return summary

    def _fetch_with_retry(self, symbol: str, timeframe: str, limit: int) -> DataSummary:
        """Retry 로직과 함께 fetch. 에러 분류로 재시도 판단."""
        last_error = None
        for attempt in range(1, self._max_retries + 1):
            try:
                logger.debug(
                    "Fetching %s %s (limit=%d), attempt %d/%d",
                    symbol, timeframe, limit, attempt, self._max_retries
                )
                return self._fetch_fresh(symbol, timeframe, limit)
            except Exception as e:
                # Fatal 에러는 재시도하지 않음
                if _is_fatal_error(e):
                    error_type = type(e).__name__
                    logger.error(
                        "Fatal error (no retry): symbol=%s, timeframe=%s, "
                        "error_type=%s, message=%s",
                        symbol, timeframe, error_type, str(e)
                    )
                    raise
                
                # Transient 에러만 재시도
                last_error = e
                if attempt < self._max_retries:
                    logger.warning(
                        "Transient error: symbol=%s, timeframe=%s, "
                        "error=%s (attempt %d/%d, retrying...)",
                        symbol, timeframe, str(e), attempt, self._max_retries
                    )
                    _backoff_with_rate_limit(e, attempt)
                else:
                    # 마지막 재시도도 transient이면 로그
                    logger.warning(
                        "Final transient error: symbol=%s, timeframe=%s, "
                        "error=%s (attempt %d/%d)",
                        symbol, timeframe, str(e), attempt, self._max_retries
                    )
        
        # 모든 재시도 실패
        error_type = type(last_error).__name__
        logger.error(
            "Fetch exhausted: symbol=%s, timeframe=%s, limit=%d, "
            "max_retries=%d, error_type=%s, message=%s",
            symbol, timeframe, limit, self._max_retries, error_type, str(last_error)
        )
        raise last_error

    def fetch_multiple(
        self,
        symbols: List[str],
        timeframe: str,
        limit: int = 500,
        max_workers: int = None,
    ) -> Dict[str, DataSummary]:
        """
        여러 심볼을 병렬로 fetch.
        
        Args:
            symbols: 심볼 리스트 (예: ["BTC/USDT", "ETH/USDT"])
            timeframe: 타임프레임 (예: "1h")
            limit: 캔들 개수
            max_workers: 스레드 풀 크기 (기본: min(32, 심볼 수 + 4))
        
        Returns:
            {symbol: DataSummary} 딕셔너리
        
        Notes:
            - 기본 fetch()와 동일한 캐싱 로직 적용
            - 오류 발생 시 해당 심볼은 건너뛰고 나머지 진행
        """
        if max_workers is None:
            max_workers = min(len(symbols) + 4, 32)
        
        results = {}
        failed = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 작업 제출
            futures = {
                executor.submit(self.fetch, symbol, timeframe, limit): symbol
                for symbol in symbols
            }
            
            # 완료된 작업 수집
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    failed[symbol] = str(e)
                    logger.warning("fetch_multiple: %s 실패 — %s", symbol, e)
        
        if failed:
            logger.info("fetch_multiple 완료: %d 성공, %d 실패", len(results), len(failed))
        
        return results

    def invalidate_cache(self, symbol=None, timeframe=None):
        """특정 심볼/타임프레임 또는 전체 캐시 무효화."""
        if symbol is None and timeframe is None:
            self._cache.clear()
        else:
            keys_to_del = [k for k in self._cache if k[0] == symbol or k[1] == timeframe]
            for k in keys_to_del:
                del self._cache[k]

    def _evict_if_needed(self):
        """캐시가 max_cache_size를 초과하면 가장 오래된 엔트리 제거 (LRU)."""
        if len(self._cache) <= self._max_cache_size:
            return
        # 타임스탬프 기준 가장 오래된 엔트리 제거
        oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
        del self._cache[oldest_key]

    def cache_stats(self) -> dict:
        """
        캐시 히트율/미스율 통계 조회.
        
        Returns:
            {
                'hit_count': int,     # 캐시 히트 수
                'miss_count': int,    # 캐시 미스 수
                'total': int,         # 총 fetch 시도 수
                'hit_rate': float,    # 히트율 (0.0 ~ 1.0)
                'cached_keys': int,   # 현재 캐시된 키 개수
            }
        """
        total = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total if total > 0 else 0.0
        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'total': total,
            'hit_rate': hit_rate,
            'cached_keys': len(self._cache),
            'max_cache_size': self._max_cache_size,
        }

    def _fetch_fresh(self, symbol: str, timeframe: str, limit: int) -> DataSummary:
        raw = self.connector.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = self._to_dataframe(raw)
        
        # 경계: 빈 DataFrame 처리
        if df.empty:
            raise ValueError(f"Empty OHLCV data for {symbol} {timeframe}")
        
        missing = self._count_missing(df, timeframe)
        anomalies = self._detect_anomalies(df)
        df = self._add_indicators(df)
        indicators = [c for c in df.columns if c not in {"open", "high", "low", "close", "volume"}]

        summary = DataSummary(
            symbol=symbol,
            timeframe=timeframe,
            candles=len(df),
            start=str(df.index[0]),
            end=str(df.index[-1]),
            missing=missing,
            indicators=indicators,
            anomalies=anomalies,
            df=df,
        )
        logger.info(
            "DataFeed: %s %s — %d candles, %d missing, %d anomalies",
            symbol,
            timeframe,
            len(df),
            missing,
            len(anomalies),
        )
        return summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_dataframe(self, raw: list) -> pd.DataFrame:
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        return df

    def _count_missing(self, df: pd.DataFrame, timeframe: str) -> int:
        freq_map = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1D"}
        freq = freq_map.get(timeframe)
        if freq is None:
            return 0
        expected = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
        return len(expected) - len(df)

    def _detect_anomalies(self, df: pd.DataFrame) -> List[str]:
        anomalies = []
        # OHLC 관계 검증
        anomalies.extend(self._validate_ohlc_relationships(df))
        # 종가 0 이하
        if (df["close"] <= 0).any():
            anomalies.append("close <= 0 detected")
        # 극단적 가격 점프 (단일 캔들 10% 이상)
        pct_change = df["close"].pct_change().abs()
        spikes = pct_change[pct_change > 0.10]
        if not spikes.empty:
            anomalies.append(f"price spike >10% at {spikes.index[0]}")
        return anomalies

    def _validate_ohlc_relationships(self, df: pd.DataFrame) -> List[str]:
        """
        OHLC 관계 검증: high >= max(open,close), low <= min(open,close)
        
        Returns:
            이상 감지 목록 (문제 없으면 빈 리스트)
        """
        issues = []
        
        # high >= max(open, close) 확인
        invalid_high = df[df["high"] < df[["open", "close"]].max(axis=1)]
        if not invalid_high.empty:
            issues.append(f"high < max(open,close) at {invalid_high.index[0]}")
        
        # low <= min(open, close) 확인
        invalid_low = df[df["low"] > df[["open", "close"]].min(axis=1)]
        if not invalid_low.empty:
            issues.append(f"low > min(open,close) at {invalid_low.index[0]}")
        
        # high >= low 확인 (기존 로직)
        inverted = df[df["high"] < df["low"]]
        if not inverted.empty:
            issues.append(f"high < low at {inverted.index[0]}")
        
        return issues

    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]
        high = df["high"]
        low = df["low"]

        # EMA
        df["ema20"] = close.ewm(span=20, adjust=False).mean()
        df["ema50"] = close.ewm(span=50, adjust=False).mean()

        # ATR (Wilder)
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["rsi14"] = 100 - (100 / (1 + rs))

        # Donchian Channel (20) — 이전 20봉 기준 (현재 봉 미포함)
        df["donchian_high"] = high.shift(1).rolling(20).max()
        df["donchian_low"] = low.shift(1).rolling(20).min()

        # SMA
        df["sma20"] = close.rolling(20, min_periods=1).mean()
        df["sma50"] = close.rolling(50, min_periods=1).mean()

        # Bollinger Bands
        df["bb_upper"] = df["sma20"] + 2 * close.rolling(20, min_periods=1).std()
        df["bb_lower"] = df["sma20"] - 2 * close.rolling(20, min_periods=1).std()

        # MACD
        df["macd"] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        # VWAP (rolling session)
        typical = (high + low + close) / 3
        df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        df["vwap20"] = (typical * df["volume"]).rolling(20, min_periods=1).sum() / df["volume"].rolling(20, min_periods=1).sum()

        # Volume SMA
        df["volume_sma20"] = df["volume"].rolling(20, min_periods=1).mean()

        # Momentum
        df["return_5"] = close.pct_change(5)

        return df
