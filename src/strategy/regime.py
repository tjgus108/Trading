"""
MarketRegimeDetector: 시장 상태(추세/횡보/고변동)를 감지하는 독립 모듈.

regime_filter.py와 달리 전략이 아니라 감지기(detector)로,
다른 전략/로테이션 매니저에서 현재 regime을 질의할 수 있다.

Regimes:
  TREND_UP   — ADX > 25, +DI > -DI, EMA20 > EMA50
  TREND_DOWN — ADX > 25, -DI > +DI, EMA20 < EMA50
  RANGING    — ADX <= 25, BB bandwidth < median
  HIGH_VOL   — ATR ratio > 1.5x 20-period mean
"""

from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd


class MarketRegime(str, Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGING = "RANGING"
    HIGH_VOL = "HIGH_VOL"


class MarketRegimeDetector:
    """시장 regime 감지기. DataFrame을 받아 현재 regime을 반환."""

    def __init__(self, adx_threshold: float = 25.0, vol_multiplier: float = 1.5):
        self.adx_threshold = adx_threshold
        self.vol_multiplier = vol_multiplier

    def detect(self, df: pd.DataFrame) -> MarketRegime:
        if df is None or len(df) < 60:
            return MarketRegime.RANGING

        close = df["close"]
        high = df["high"]
        low = df["low"]

        adx, plus_di, minus_di = self._adx(high, low, close, period=14)
        atr_regime = self._atr_regime(high, low, close)
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        cur_adx = float(adx.iloc[-2]) if not pd.isna(adx.iloc[-2]) else 0.0
        cur_plus = float(plus_di.iloc[-2]) if not pd.isna(plus_di.iloc[-2]) else 0.0
        cur_minus = float(minus_di.iloc[-2]) if not pd.isna(minus_di.iloc[-2]) else 0.0
        cur_ema20 = float(ema20.iloc[-2])
        cur_ema50 = float(ema50.iloc[-2])

        if atr_regime:
            return MarketRegime.HIGH_VOL

        if cur_adx > self.adx_threshold:
            if cur_plus > cur_minus and cur_ema20 > cur_ema50:
                return MarketRegime.TREND_UP
            elif cur_minus > cur_plus and cur_ema20 < cur_ema50:
                return MarketRegime.TREND_DOWN

        return MarketRegime.RANGING

    def detect_history(self, df: pd.DataFrame, lookback: int = 30) -> list:
        """최근 lookback 캔들의 regime 이력 반환."""
        if df is None or len(df) < 60 + lookback:
            return []
        regimes = []
        for i in range(lookback):
            end = len(df) - lookback + i + 1
            sub = df.iloc[:end]
            regimes.append(self.detect(sub))
        return regimes

    def regime_summary(self, df: pd.DataFrame, lookback: int = 30) -> dict:
        """최근 lookback 캔들의 regime 분포 반환."""
        history = self.detect_history(df, lookback)
        if not history:
            return {}
        total = len(history)
        return {r.value: history.count(r) / total for r in MarketRegime}

    def _adx(self, high, low, close, period=14):
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)

        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr.replace(0, np.nan))
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr.replace(0, np.nan))
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
        adx = dx.rolling(period).mean()
        return adx, plus_di, minus_di

    def _atr_regime(self, high, low, close) -> bool:
        """현재 ATR이 20-period 평균 대비 vol_multiplier 배 초과인지."""
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean()
        atr_ratio = atr14 / close.replace(0, np.nan)
        mean20 = atr_ratio.rolling(20).mean()

        cur = float(atr_ratio.iloc[-2]) if not pd.isna(atr_ratio.iloc[-2]) else 0.0
        avg = float(mean20.iloc[-2]) if not pd.isna(mean20.iloc[-2]) else float("inf")
        return cur > avg * self.vol_multiplier if avg > 0 else False

    def _atr_regime_series(self, high, low, close) -> list:
        """전체 시리즈에 대해 HIGH_VOL 여부 반환."""
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr14 = tr.rolling(14).mean()
        atr_ratio = atr14 / close.replace(0, np.nan)
        mean20 = atr_ratio.rolling(20).mean()
        result = []
        for i in range(len(close)):
            r = atr_ratio.iloc[i]
            m = mean20.iloc[i]
            if pd.isna(r) or pd.isna(m) or m <= 0:
                result.append(False)
            else:
                result.append(r > m * self.vol_multiplier)
        return result
