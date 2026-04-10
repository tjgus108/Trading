"""
VolumeWeightedRSIStrategy — 거래량으로 가중된 RSI.

- diff = close.diff()
- vol_weight = volume / volume.rolling(14).mean()
- weighted_gain = (diff.clip(lower=0) * vol_weight).rolling(14).sum()
- weighted_loss = ((-diff.clip(upper=0)) * vol_weight).rolling(14).sum()
- rs = weighted_gain / (weighted_loss + 1e-10)
- vrsi = 100 - 100 / (1 + rs)
- BUY:  vrsi crosses above 30 (prev < 30, now >= 30)
- SELL: vrsi crosses below 70 (prev > 70, now <= 70)
- confidence: vrsi < 20 (BUY) or vrsi > 80 (SELL) -> HIGH, else MEDIUM
- 최소 행: 20
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROLL = 14


def _calc_vrsi(close: pd.Series, volume: pd.Series) -> pd.Series:
    diff = close.diff()
    vol_ma = volume.rolling(_ROLL).mean()
    vol_weight = volume / (vol_ma + 1e-10)
    weighted_gain = (diff.clip(lower=0) * vol_weight).rolling(_ROLL).sum()
    weighted_loss = ((-diff.clip(upper=0)) * vol_weight).rolling(_ROLL).sum()
    rs = weighted_gain / (weighted_loss + 1e-10)
    return 100 - 100 / (1 + rs)


class VolumeWeightedRSIStrategy(BaseStrategy):
    name = "volume_weighted_rsi"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (minimum 20 rows required)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]
        volume = df["volume"]

        vrsi = _calc_vrsi(close, volume)
        vrsi_now = float(vrsi.iloc[idx])
        vrsi_prev = float(vrsi.iloc[idx - 1])

        if pd.isna(vrsi_now) or pd.isna(vrsi_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(close.iloc[idx]),
                reasoning="Insufficient data: VRSI is NaN",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(close.iloc[idx])

        # BUY: crosses above 30
        if vrsi_prev < 30 and vrsi_now >= 30:
            conf = Confidence.HIGH if vrsi_now < 20 or vrsi_prev < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VRSI crossed above 30: {vrsi_prev:.2f} -> {vrsi_now:.2f}",
                invalidation="VRSI drops back below 30",
                bull_case=f"VRSI={vrsi_now:.2f}, oversold exit",
                bear_case="Further downside possible",
            )

        # SELL: crosses below 70
        if vrsi_prev > 70 and vrsi_now <= 70:
            conf = Confidence.HIGH if vrsi_prev > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VRSI crossed below 70: {vrsi_prev:.2f} -> {vrsi_now:.2f}",
                invalidation="VRSI rises back above 70",
                bull_case="Short-term bounce possible",
                bear_case=f"VRSI={vrsi_now:.2f}, overbought exit",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"VRSI neutral: {vrsi_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
