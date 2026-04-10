"""
VolatilityMeanReversionStrategy:
- 변동성 평균 회귀: 변동성 급등 후 정상화 예상
- hist_vol = close.pct_change().rolling(10).std() * sqrt(252)
- vol_ratio = hist_vol / hist_vol.rolling(30).mean()
- BUY: vol_ratio < 0.5 AND close > SMA20 (저변동성 + 상승 추세)
- SELL: vol_ratio < 0.5 AND close < SMA20
- BUY (high vol recovery): vol_ratio > 2 AND rsi14 < 40
- SELL (high vol recovery): vol_ratio > 2 AND rsi14 > 60
- confidence HIGH: vol_ratio < 0.3 or vol_ratio > 3
- 최소 행: 45
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 45


def _wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class VolatilityMeanReversionStrategy(BaseStrategy):
    name = "vol_mean_rev"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        hist_vol = close.pct_change().rolling(10).std() * np.sqrt(252)
        vol_mean = hist_vol.rolling(30).mean()
        vol_ratio = hist_vol / vol_mean.replace(0, 1e-10)
        sma20 = close.rolling(20).mean()
        rsi14 = _wilder_rsi(close, 14)

        idx = len(df) - 2
        vr_raw = vol_ratio.iloc[idx]
        price = float(close.iloc[idx])
        sma = float(sma20.iloc[idx])
        rsi_raw = rsi14.iloc[idx]

        # NaN 체크
        if pd.isna(vr_raw) or pd.isna(rsi_raw) or pd.isna(sma):
            return self._hold(df, "Insufficient indicator data")

        vr = float(vr_raw)
        rsi = float(rsi_raw)

        is_high = vr > 3 or vr < 0.3
        context = f"close={price:.4f} sma20={sma:.4f} vol_ratio={vr:.3f} rsi14={rsi:.2f}"

        # 저변동성 구간
        if vr < 0.5:
            if price > sma:
                conf = Confidence.HIGH if is_high else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=price,
                    reasoning=f"저변동성 BUY: vol_ratio={vr:.3f}<0.5, close>SMA20",
                    invalidation="vol_ratio >= 0.5 또는 close <= SMA20",
                    bull_case=context,
                    bear_case=context,
                )
            else:
                conf = Confidence.HIGH if is_high else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=price,
                    reasoning=f"저변동성 SELL: vol_ratio={vr:.3f}<0.5, close<SMA20",
                    invalidation="vol_ratio >= 0.5 또는 close >= SMA20",
                    bull_case=context,
                    bear_case=context,
                )

        # 고변동성 구간 (과매도 회복 기대)
        if vr > 2:
            if rsi < 40:
                conf = Confidence.HIGH if is_high else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=price,
                    reasoning=f"고변동성 회복 BUY: vol_ratio={vr:.3f}>2, rsi14={rsi:.2f}<40",
                    invalidation="rsi14 >= 40",
                    bull_case=context,
                    bear_case=context,
                )
            if rsi > 60:
                conf = Confidence.HIGH if is_high else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=price,
                    reasoning=f"고변동성 회복 SELL: vol_ratio={vr:.3f}>2, rsi14={rsi:.2f}>60",
                    invalidation="rsi14 <= 60",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        price = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
