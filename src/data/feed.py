"""
DataFeed: OHLCV 수집 + 기술 지표 계산.
data-agent가 이 모듈을 사용한다.
"""

import logging
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.exchange.connector import ExchangeConnector

logger = logging.getLogger(__name__)


@dataclass
class DataSummary:
    symbol: str
    timeframe: str
    candles: int
    start: str
    end: str
    missing: int
    indicators: list[str]
    anomalies: list[str]
    df: pd.DataFrame = field(repr=False)


class DataFeed:
    def __init__(self, connector: ExchangeConnector, cache_ttl: int = 60):
        self.connector = connector
        self._cache: dict = {}       # (symbol, timeframe, limit) → (DataSummary, timestamp)
        self._cache_ttl = cache_ttl  # 초

    def fetch(self, symbol: str, timeframe: str, limit: int = 500) -> DataSummary:
        key = (symbol, timeframe, limit)
        now = time.time()
        if key in self._cache:
            cached_summary, ts = self._cache[key]
            if now - ts < self._cache_ttl:
                return cached_summary  # 캐시 히트
        # 캐시 미스: 실제 fetch
        summary = self._fetch_fresh(symbol, timeframe, limit)
        self._cache[key] = (summary, now)
        return summary

    def invalidate_cache(self, symbol=None, timeframe=None):
        """특정 심볼/타임프레임 또는 전체 캐시 무효화."""
        if symbol is None and timeframe is None:
            self._cache.clear()
        else:
            keys_to_del = [k for k in self._cache if k[0] == symbol or k[1] == timeframe]
            for k in keys_to_del:
                del self._cache[k]

    def _fetch_fresh(self, symbol: str, timeframe: str, limit: int) -> DataSummary:
        raw = self.connector.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = self._to_dataframe(raw)
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

    def _detect_anomalies(self, df: pd.DataFrame) -> list[str]:
        anomalies = []
        # 캔들 내 고/저 역전
        inverted = df[df["high"] < df["low"]]
        if not inverted.empty:
            anomalies.append(f"high<low at {inverted.index[0]}")
        # 종가 0 이하
        if (df["close"] <= 0).any():
            anomalies.append("close <= 0 detected")
        # 극단적 가격 점프 (단일 캔들 10% 이상)
        pct_change = df["close"].pct_change().abs()
        spikes = pct_change[pct_change > 0.10]
        if not spikes.empty:
            anomalies.append(f"price spike >10% at {spikes.index[0]}")
        return anomalies

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

        # VWAP (rolling session)
        typical = (high + low + close) / 3
        df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()

        return df
