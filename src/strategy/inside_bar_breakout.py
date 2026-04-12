"""
InsideBarBreakoutStrategy: Inside Bar 돌파 확인 전략.

기존 inside_bar.py(단순 inside bar 감지) 차별화: Mother bar 기준 돌파 확인.
- Mother bar: prev-2 봉 (idx-2)
- Inside bar: prev-1 봉 (high < mother.high AND low > mother.low)
- Breakout: current 봉이 inside bar 범위가 아닌 **mother bar** 범위 이탈
- BUY:  inside_bar_confirmed AND current.close > mother.high
- SELL: inside_bar_confirmed AND current.close < mother.low
- confidence: mother bar range > ATR14 * 1.5 → HIGH, else MEDIUM
- 최소 행: 10
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


class InsideBarBreakoutStrategy(BaseStrategy):
    name = "inside_bar_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2      # current (완성된 마지막 봉)
        ib_idx = idx - 1       # inside bar 후보 (prev-1)
        mother_idx = idx - 2   # mother bar (prev-2)

        if mother_idx < 0:
            return self._hold(df, "Insufficient data")

        mother_high = float(df["high"].iloc[mother_idx])
        mother_low = float(df["low"].iloc[mother_idx])
        ib_high = float(df["high"].iloc[ib_idx])
        ib_low = float(df["low"].iloc[ib_idx])

        is_inside = ib_high < mother_high and ib_low > mother_low

        close_now = float(df["close"].iloc[idx])
        atr = float(df["atr14"].iloc[idx])
        mother_range = mother_high - mother_low

        context = (
            f"inside={is_inside}, close={close_now:.2f}, "
            f"mother=[{mother_low:.2f},{mother_high:.2f}], "
            f"ib=[{ib_low:.2f},{ib_high:.2f}], "
            f"mother_range={mother_range:.4f}, ATR={atr:.4f}"
        )

        if not is_inside:
            return self._hold(
                df,
                f"No inside bar: ib=[{ib_low:.2f},{ib_high:.2f}] not inside mother=[{mother_low:.2f},{mother_high:.2f}]",
                context, context,
            )

        conf = Confidence.HIGH if atr > 0 and mother_range > atr * 1.5 else Confidence.MEDIUM

        # BUY: close > mother.high
        if close_now > mother_high:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"InsideBarBreakout BUY: close({close_now:.2f})>mother_high({mother_high:.2f}), "
                    f"mother_range={mother_range:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back below mother_high ({mother_high:.2f})",
                bull_case=context,
                bear_case=context,
            )

        # SELL: close < mother.low
        if close_now < mother_low:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"InsideBarBreakout SELL: close({close_now:.2f})<mother_low({mother_low:.2f}), "
                    f"mother_range={mother_range:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back above mother_low ({mother_low:.2f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"Inside bar confirmed but no mother bar breakout: close={close_now:.2f} within [{mother_low:.2f},{mother_high:.2f}]",
            context, context,
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
