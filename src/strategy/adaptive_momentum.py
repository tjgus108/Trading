"""
AdaptiveMomentumStrategy — 시장 변동성에 따라 look-back이 동적으로 변하는 모멘텀.

- atr14 = rolling ATR(14)
- vol_rank = ((atr14/close) - min) / (max - min)  rolling(50) percentile rank
- lookback: vol_rank > 0.7 -> 5봉, vol_rank < 0.3 -> 20봉, else -> 10봉
- adaptive_mom: (close[idx] - close[idx-lookback]) / close[idx-lookback]
- BUY:  mom > 0.02 AND mom > mom_prev
- SELL: mom < -0.02 AND mom < mom_prev
- confidence: |mom| > 0.05 -> HIGH, else MEDIUM
- 최소 행: 60
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 60


def _calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


class AdaptiveMomentumStrategy(BaseStrategy):
    name = "adaptive_momentum"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (minimum 60 rows required)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]

        atr14 = _calc_atr(df, 14)
        ratio = atr14 / (close + 1e-10)
        ratio_min = ratio.rolling(50).min()
        ratio_max = ratio.rolling(50).max()
        denom = ratio_max - ratio_min
        # avoid division by zero
        vol_rank = (ratio - ratio_min) / denom.where(denom != 0, other=1.0)

        vr_val = float(vol_rank.iloc[idx]) if not pd.isna(vol_rank.iloc[idx]) else 0.5
        if vr_val > 0.7:
            lookback = 5
        elif vr_val < 0.3:
            lookback = 20
        else:
            lookback = 10

        if idx >= lookback:
            mom = (float(close.iloc[idx]) - float(close.iloc[idx - lookback])) / float(close.iloc[idx - lookback])
            if idx - 1 >= lookback:
                mom_prev = (float(close.iloc[idx - 1]) - float(close.iloc[idx - 1 - lookback])) / float(close.iloc[idx - 1 - lookback])
            else:
                mom_prev = 0.0
        else:
            mom = 0.0
            mom_prev = 0.0

        entry = float(close.iloc[idx])

        if mom > 0.02 and mom > mom_prev:
            conf = Confidence.HIGH if abs(mom) > 0.05 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Adaptive momentum BUY: mom={mom:.4f} > 0.02 and accelerating (lookback={lookback})",
                invalidation="Momentum drops below 0.02 or decelerates",
                bull_case=f"mom={mom:.4f}, vol_rank={vr_val:.2f}",
                bear_case="Momentum may fade",
            )

        if mom < -0.02 and mom < mom_prev:
            conf = Confidence.HIGH if abs(mom) > 0.05 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Adaptive momentum SELL: mom={mom:.4f} < -0.02 and decelerating (lookback={lookback})",
                invalidation="Momentum rises above -0.02 or reverses",
                bull_case="Momentum may recover",
                bear_case=f"mom={mom:.4f}, vol_rank={vr_val:.2f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Adaptive momentum HOLD: mom={mom:.4f} (lookback={lookback}, vol_rank={vr_val:.2f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )
