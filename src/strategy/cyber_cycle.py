"""
CyberCycleStrategy: Ehlers Cyber Cycle 기반 전략.
가격의 주기적 성분을 추출하여 cycle이 trigger(shift(1))를 교차할 때 신호 생성.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_WARMUP = 10


class CyberCycleStrategy(BaseStrategy):
    name = "cyber_cycle"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: need {_MIN_ROWS} rows, got {len(df)}")

        smooth = (
            df["close"]
            + 2 * df["close"].shift(1)
            + 2 * df["close"].shift(2)
            + df["close"].shift(3)
        ) / 6

        alpha = 0.07
        cycle = pd.Series(0.0, index=df.index)
        for i in range(4, len(df)):
            s_i = float(smooth.iloc[i]) if not pd.isna(smooth.iloc[i]) else 0.0
            s_i1 = float(smooth.iloc[i - 1]) if not pd.isna(smooth.iloc[i - 1]) else 0.0
            s_i2 = float(smooth.iloc[i - 2]) if not pd.isna(smooth.iloc[i - 2]) else 0.0
            cycle.iloc[i] = (
                (1 - 0.5 * alpha) ** 2 * (s_i - 2 * s_i1 + s_i2)
                + 2 * (1 - alpha) * float(cycle.iloc[i - 1])
                - (1 - alpha) ** 2 * float(cycle.iloc[i - 2])
            )

        trigger = cycle.shift(1)

        idx = len(df) - 2

        # Warmup suppression
        if idx < _WARMUP:
            return self._hold(df, "Warmup period — suppressing signal")

        if pd.isna(cycle.iloc[idx]) or pd.isna(trigger.iloc[idx]) or pd.isna(cycle.iloc[idx - 1]) or pd.isna(trigger.iloc[idx - 1]):
            return self._hold(df, "NaN in Cyber Cycle values")

        cycle_cur = float(cycle.iloc[idx])
        trigger_cur = float(trigger.iloc[idx])
        cycle_prev = float(cycle.iloc[idx - 1])
        trigger_prev = float(trigger.iloc[idx - 1])

        entry = float(df["close"].iloc[-2])

        cross_up = cycle_prev < trigger_prev and cycle_cur > trigger_cur
        cross_down = cycle_prev > trigger_prev and cycle_cur < trigger_cur

        # Confidence: HIGH if abs(cycle) > rolling 20-period std
        lookback = min(20, idx)
        cycle_std = float(cycle.iloc[max(0, idx - lookback): idx + 1].std())
        high_conf = cycle_std > 0 and abs(cycle_cur) > cycle_std

        if cross_up and cycle_cur < 0:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Cyber Cycle cross up in negative zone. "
                    f"cycle={cycle_cur:.6f} crossed above trigger={trigger_cur:.6f} "
                    f"(prev cycle={cycle_prev:.6f}, trigger={trigger_prev:.6f}). "
                    f"cycle < 0."
                ),
                invalidation="cycle crosses below trigger again",
                bull_case=f"cycle={cycle_cur:.6f} rising from negative zone",
                bear_case=f"cycle={cycle_cur:.6f} may re-enter negative",
            )

        if cross_down and cycle_cur > 0:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Cyber Cycle cross down in positive zone. "
                    f"cycle={cycle_cur:.6f} crossed below trigger={trigger_cur:.6f} "
                    f"(prev cycle={cycle_prev:.6f}, trigger={trigger_prev:.6f}). "
                    f"cycle > 0."
                ),
                invalidation="cycle crosses above trigger again",
                bull_case=f"cycle={cycle_cur:.6f} may reverse upward",
                bear_case=f"cycle={cycle_cur:.6f} falling from positive zone",
            )

        return self._hold(df, f"No Cyber Cycle crossover. cycle={cycle_cur:.6f}, trigger={trigger_cur:.6f}")

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
