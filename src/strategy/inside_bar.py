"""
Inside Bar Breakout 전략.

Inside Bar: 이전 봉의 고저 범위 안에 있는 봉 다음 돌파 시 신호.
- BUY:  idx-1이 inside bar AND 현재 close > idx-1 봉 high
- SELL: idx-1이 inside bar AND 현재 close < idx-1 봉 low
- HOLD: inside bar 없거나 돌파 없음
- confidence: HIGH if 모봉(idx-2) 범위 >= ATR * 1.5, MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class InsideBarStrategy(BaseStrategy):
    name = "inside_bar"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 5:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        ib_idx = idx - 1   # inside bar 후보
        mother_idx = idx - 2  # 모봉

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
        entry = close_now

        bull_case = (
            f"InsideBar={is_inside}, close={close_now:.2f} > ib_high={ib_high:.2f}, "
            f"mother_range={mother_range:.4f}, ATR={atr:.4f}"
        )
        bear_case = (
            f"InsideBar={is_inside}, close={close_now:.2f} < ib_low={ib_low:.2f}, "
            f"mother_range={mother_range:.4f}, ATR={atr:.4f}"
        )

        if not is_inside:
            return self._hold(df, f"No inside bar: ib=[{ib_low:.2f},{ib_high:.2f}] not inside mother=[{mother_low:.2f},{mother_high:.2f}]")

        # confidence: 모봉 범위가 ATR의 1.5배 이상이면 HIGH
        conf = Confidence.HIGH if atr > 0 and mother_range >= atr * 1.5 else Confidence.MEDIUM

        # 상향 돌파
        if close_now > ib_high:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Inside bar breakout UP: close({close_now:.2f}) > ib_high({ib_high:.2f}), "
                    f"mother_range={mother_range:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back below ib_high ({ib_high:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 하향 돌파
        if close_now < ib_low:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Inside bar breakout DOWN: close({close_now:.2f}) < ib_low({ib_low:.2f}), "
                    f"mother_range={mother_range:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back above ib_low ({ib_low:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"Inside bar found but no breakout: close={close_now:.2f} within [{ib_low:.2f}, {ib_high:.2f}]")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
