"""
GapFillStrategy: 갭 역방향 채우기 전략.
- gap_strategy.py와 반대: 갭이 결국 메워진다는 가정
- Gap Down 후 회복 → BUY (gap fill 기대)
- Gap Up 후 하락 → SELL (gap fill 기대)
- confidence: gap > 1.5% → HIGH
- 최소 행: 5
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 5
_GAP_THRESHOLD = 0.005   # 0.5%
_GAP_HIGH = 0.015        # 1.5%


class GapFillStrategy(BaseStrategy):
    name = "gap_fill"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        curr = self._last(df)
        prev = df.iloc[-3]  # _last = iloc[-2], 그 이전 봉

        open_now = float(curr["open"])
        close_now = float(curr["close"])
        prev_close = float(prev["close"])

        if abs(prev_close) < 1e-10:
            return self._hold(df, "Invalid prev_close")

        gap_size = (open_now - prev_close) / prev_close  # 양수=갭업, 음수=갭다운
        abs_gap = abs(gap_size)

        gap_up = gap_size > _GAP_THRESHOLD
        gap_down = gap_size < -_GAP_THRESHOLD

        if abs_gap > _GAP_HIGH:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        # BUY: 갭다운 후 회복 (close > open → 반등 시작)
        if gap_down and close_now > open_now:
            reason = (
                f"Gap Down {abs_gap*100:.2f}% (open={open_now:.4f} < prev_close={prev_close:.4f}), "
                f"recovery candle (close={close_now:.4f} > open={open_now:.4f}), gap fill expected"
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close below open ({open_now:.4f})",
                bull_case=f"Gap fill target: prev_close {prev_close:.4f}",
                bear_case="Gap may extend further down",
            )

        # SELL: 갭업 후 하락 (close < open → 갭 채우기 시작)
        if gap_up and close_now < open_now:
            reason = (
                f"Gap Up {abs_gap*100:.2f}% (open={open_now:.4f} > prev_close={prev_close:.4f}), "
                f"reversal candle (close={close_now:.4f} < open={open_now:.4f}), gap fill expected"
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close above open ({open_now:.4f})",
                bull_case="Gap up momentum may continue",
                bear_case=f"Gap fill target: prev_close {prev_close:.4f}",
            )

        reason = (
            f"No gap fill signal: gap_size={gap_size*100:.2f}%, "
            f"gap_up={gap_up}, gap_down={gap_down}, "
            f"close={'>' if close_now > open_now else '<='} open"
        )
        return self._hold(df, reason)

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df.iloc[-2]["close"]) if len(df) >= 2 else float(df.iloc[-1]["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
