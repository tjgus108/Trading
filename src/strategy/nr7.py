"""
NR7 (Narrow Range 7) Breakout 전략.

NR7: 최근 7봉 중 가장 좁은 레인지인 봉 다음 날 돌파 시 신호.
- BUY:  이전 봉이 NR7 AND 현재 close > 이전 봉 high
- SELL: 이전 봉이 NR7 AND 현재 close < 이전 봉 low
- HOLD: NR7 없거나 돌파 없음
- confidence: HIGH if 돌파폭 > ATR * 0.5, MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class NR7Strategy(BaseStrategy):
    name = "nr7"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 10:
            return self._hold(df, "Insufficient data for NR7")

        idx = len(df) - 2
        nr7_idx = idx - 1  # inside bar 후보 (NR7 여부 판단 대상)

        if nr7_idx < 6:
            return self._hold(df, "Insufficient data for NR7")

        ranges = df["high"] - df["low"]
        curr_range = float(ranges.iloc[nr7_idx])
        prev_7_ranges = ranges.iloc[nr7_idx - 6: nr7_idx]  # 직전 6봉 (총 7봉 비교)

        is_nr7 = curr_range < float(prev_7_ranges.min())

        close_now = float(df["close"].iloc[idx])
        high_prev = float(df["high"].iloc[nr7_idx])
        low_prev = float(df["low"].iloc[nr7_idx])
        atr = float(df["atr14"].iloc[idx])
        entry = close_now

        bull_case = (
            f"NR7={is_nr7}, close={close_now:.2f} > prev_high={high_prev:.2f}, "
            f"ATR={atr:.4f}, breakout={close_now - high_prev:.4f}"
        )
        bear_case = (
            f"NR7={is_nr7}, close={close_now:.2f} < prev_low={low_prev:.2f}, "
            f"ATR={atr:.4f}, breakout={low_prev - close_now:.4f}"
        )

        if not is_nr7:
            return self._hold(df, f"No NR7 at bar {nr7_idx}: range={curr_range:.4f} not smallest in 7")

        # 상향 돌파
        if close_now > high_prev:
            breakout = close_now - high_prev
            conf = Confidence.HIGH if atr > 0 and breakout > atr * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"NR7 breakout UP: close({close_now:.2f}) > prev_high({high_prev:.2f}), "
                    f"breakout={breakout:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back below prev_high ({high_prev:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 하향 돌파
        if close_now < low_prev:
            breakout = low_prev - close_now
            conf = Confidence.HIGH if atr > 0 and breakout > atr * 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"NR7 breakout DOWN: close({close_now:.2f}) < prev_low({low_prev:.2f}), "
                    f"breakout={breakout:.4f}, ATR={atr:.4f}, conf={conf.value}"
                ),
                invalidation=f"Close back above prev_low ({low_prev:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"NR7 found but no breakout: close={close_now:.2f} within [{low_prev:.2f}, {high_prev:.2f}]")

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
