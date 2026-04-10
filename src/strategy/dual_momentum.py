"""
DualMomentumStrategy: Gary Antonacci Dual Momentum 간소화
- BUY:  absolute_momentum > 0 AND relative_momentum > rel_ma AND abs_ma > 0
- SELL: absolute_momentum < 0 AND relative_momentum < rel_ma AND abs_ma < 0
- confidence: HIGH if absolute_momentum > rolling(20).std() else MEDIUM
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class DualMomentumStrategy(BaseStrategy):
    name = "dual_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        absolute_momentum = close.pct_change(12, fill_method=None)
        relative_momentum = close.pct_change(6, fill_method=None)
        abs_ma = absolute_momentum.rolling(3, min_periods=1).mean()
        rel_ma = relative_momentum.rolling(3, min_periods=1).mean()
        abs_std = absolute_momentum.rolling(20, min_periods=1).std()

        idx = len(df) - 2
        last = df.iloc[idx]

        am = absolute_momentum.iloc[idx]
        rm = relative_momentum.iloc[idx]
        am_ma = abs_ma.iloc[idx]
        rm_ma = rel_ma.iloc[idx]
        std = abs_std.iloc[idx]

        if any(pd.isna(v) for v in [am, rm, am_ma, rm_ma]):
            return self._hold(df, "NaN in indicators")

        close_val = float(last["close"])
        context = f"abs_mom={am:.4f} rel_mom={rm:.4f} abs_ma={am_ma:.4f} rel_ma={rm_ma:.4f}"

        if am > 0 and rm > rm_ma and am_ma > 0:
            confidence = Confidence.HIGH if (not pd.isna(std) and am > std) else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Dual Momentum BUY: abs_mom={am:.4f}>0, rel_mom={rm:.4f}>rel_ma={rm_ma:.4f}, abs_ma={am_ma:.4f}>0",
                invalidation="abs_momentum turns negative or rel_momentum drops below rel_ma",
                bull_case=context,
                bear_case=context,
            )

        if am < 0 and rm < rm_ma and am_ma < 0:
            confidence = Confidence.HIGH if (not pd.isna(std) and am < -std) else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Dual Momentum SELL: abs_mom={am:.4f}<0, rel_mom={rm:.4f}<rel_ma={rm_ma:.4f}, abs_ma={am_ma:.4f}<0",
                invalidation="abs_momentum turns positive or rel_momentum rises above rel_ma",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No dual momentum signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close_val = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
