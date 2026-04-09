"""
Gap Strategy:
- Gap Up (갭 상승) + 볼륨 확인 → BUY
- Gap Down (갭 하락) + 볼륨 확인 → SELL
- confidence: HIGH if Gap Size > 1.5%, MEDIUM if > 0.5%
- 최소 25행, idx = len(df) - 2
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_GAP_MEDIUM = 0.5
_GAP_HIGH = 1.5


class GapStrategy(BaseStrategy):
    name = "gap_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]

        open_now = float(curr["open"])
        close_now = float(curr["close"])
        prev_close = float(prev["close"])
        vol_now = float(curr["volume"])
        avg_vol = float(df["volume"].iloc[idx - 20:idx].mean())

        gap_size = abs(open_now - prev_close) / max(abs(prev_close), 1e-10) * 100
        gap_up = open_now > prev_close and gap_size > _GAP_MEDIUM
        gap_down = open_now < prev_close and gap_size > _GAP_MEDIUM
        vol_ok = vol_now > avg_vol

        if gap_size > _GAP_HIGH:
            confidence = Confidence.HIGH
        elif gap_size > _GAP_MEDIUM:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        # BUY: Gap Up + 갭 방향 유지 (close > open) + 볼륨 확인
        if gap_up and close_now > open_now and vol_ok:
            reason = (
                f"Gap Up {gap_size:.2f}% (open={open_now:.2f} > prev_close={prev_close:.2f}), "
                f"bullish candle, vol={vol_now:.0f} > avg={avg_vol:.0f}"
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close below prev_close ({prev_close:.2f})",
                bull_case=f"Gap Up momentum {gap_size:.2f}%",
                bear_case="Gap may fill (mean reversion)",
            )

        # SELL: Gap Down + 갭 방향 유지 (close < open) + 볼륨 확인
        if gap_down and close_now < open_now and vol_ok:
            reason = (
                f"Gap Down {gap_size:.2f}% (open={open_now:.2f} < prev_close={prev_close:.2f}), "
                f"bearish candle, vol={vol_now:.0f} > avg={avg_vol:.0f}"
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=reason,
                invalidation=f"Close above prev_close ({prev_close:.2f})",
                bull_case="Gap may fill (mean reversion)",
                bear_case=f"Gap Down momentum {gap_size:.2f}%",
            )

        reason = (
            f"No gap signal: gap_size={gap_size:.2f}%, "
            f"gap_up={gap_up}, gap_down={gap_down}, vol_ok={vol_ok}, "
            f"close={'>' if close_now > open_now else '<'} open"
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
