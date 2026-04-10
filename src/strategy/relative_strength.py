"""
RelativeStrengthStrategy:
- roc_n = close.pct_change(n) (기본 n=14)
- roc_avg = roc_n.rolling(20).mean()
- roc_std = roc_n.rolling(20).std()
- BUY: roc_n > roc_avg + roc_std (강한 모멘텀)
- SELL: roc_n < roc_avg - roc_std (약한 모멘텀)
- confidence: HIGH if |roc_n - roc_avg| > 2 * roc_std else MEDIUM
- 최소 40행 필요
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_ROC_N = 14
_ROLL = 20
_MIN_ROWS = 40


class RelativeStrengthStrategy(BaseStrategy):
    name = "relative_strength"

    def __init__(self, n: int = _ROC_N) -> None:
        self._n = n

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for relative_strength",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        roc_n = df["close"].pct_change(self._n)
        roc_avg = roc_n.rolling(_ROLL).mean()
        roc_std = roc_n.rolling(_ROLL).std()

        val = roc_n.iloc[idx]
        avg = roc_avg.iloc[idx]
        std = roc_std.iloc[idx]

        if pd.isna(val) or pd.isna(avg) or pd.isna(std) or std == 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for relative_strength (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(df["close"].iloc[idx])
        diff = abs(val - avg)
        conf = Confidence.HIGH if diff > 2 * std else Confidence.MEDIUM

        if val > avg + std:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"상대 강도 BUY: roc={val:.4f} > avg+std={avg + std:.4f}",
                invalidation="roc_n이 roc_avg 아래로 하락 시",
                bull_case=f"강한 모멘텀: roc {val:.4f}, avg {avg:.4f}",
                bear_case="모멘텀 약화 시 반전 가능",
            )

        if val < avg - std:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"상대 강도 SELL: roc={val:.4f} < avg-std={avg - std:.4f}",
                invalidation="roc_n이 roc_avg 위로 반등 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"약한 모멘텀: roc {val:.4f}, avg {avg:.4f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"상대 강도 HOLD: roc={val:.4f}, avg={avg:.4f}, std={std:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
