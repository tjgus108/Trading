"""
AdaptiveCycleStrategy: 시장 사이클 감지 기반 전략.
Rolling 극값으로 사이클 위치(0=저점, 1=고점)를 계산하여 사이클 위상에 따라 매매.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15


class AdaptiveCycleStrategy(BaseStrategy):
    name = "adaptive_cycle"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: need {_MIN_ROWS} rows, got {len(df)}")

        window = 10
        rolling_max = df["high"].rolling(window).max()
        rolling_min = df["low"].rolling(window).min()

        cycle_range = rolling_max - rolling_min
        cycle_pos = (df["close"] - rolling_min) / cycle_range.replace(0, 0.0001)
        cycle_dir = cycle_pos.diff()

        idx = len(df) - 2

        if pd.isna(cycle_pos.iloc[idx]) or pd.isna(cycle_dir.iloc[idx]):
            return self._hold(df, "NaN in Adaptive Cycle values")

        pos = float(cycle_pos.iloc[idx])
        direction = float(cycle_dir.iloc[idx])
        entry = float(df["close"].iloc[-2])

        is_buy = pos < 0.2 and direction > 0
        is_sell = pos > 0.8 and direction < 0

        if is_buy:
            confidence = Confidence.HIGH if pos < 0.1 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Adaptive Cycle near cycle low, turning up. "
                    f"cycle_pos={pos:.4f} (<0.2), cycle_dir={direction:.4f} (>0)."
                ),
                invalidation="cycle_pos rises above 0.5 without follow-through",
                bull_case=f"cycle_pos={pos:.4f} near bottom, upward momentum",
                bear_case=f"cycle_pos={pos:.4f} may continue lower",
            )

        if is_sell:
            confidence = Confidence.HIGH if pos > 0.9 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Adaptive Cycle near cycle high, turning down. "
                    f"cycle_pos={pos:.4f} (>0.8), cycle_dir={direction:.4f} (<0)."
                ),
                invalidation="cycle_pos falls below 0.5 without follow-through",
                bull_case=f"cycle_pos={pos:.4f} may resume upward",
                bear_case=f"cycle_pos={pos:.4f} near top, downward momentum",
            )

        return self._hold(df, f"Cycle in mid-range. cycle_pos={pos:.4f}, cycle_dir={direction:.4f}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
