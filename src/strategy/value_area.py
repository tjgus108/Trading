"""
ValueArea 전략:
- VWAP 기반 Value Area(VA) 이탈 후 재진입 시 매매
- BUY:  prev_close < va_low AND curr_close > va_low (재진입)
- SELL: prev_close > va_high AND curr_close < va_high (재진입)
- HOLD: 그 외
- confidence: HIGH if |close - vwap| < std * 0.3 else MEDIUM
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_VA_MULT = 0.7
_HIGH_CONF_MULT = 0.3


class ValueAreaStrategy(BaseStrategy):
    name = "value_area"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_safe(df, "Insufficient data for ValueArea (need 25 rows)")

        close = df["close"]
        volume = df["volume"]

        vwap = (close * volume).rolling(_PERIOD).sum() / volume.rolling(_PERIOD).sum()
        std = close.rolling(_PERIOD).std()
        va_high = vwap + std * _VA_MULT
        va_low = vwap - std * _VA_MULT

        idx = len(df) - 2

        # NaN guard
        if idx < 1:
            return self._hold_safe(df, "Insufficient data for ValueArea (idx < 1)")

        for val, label in [
            (vwap.iloc[idx], "vwap"),
            (std.iloc[idx], "std"),
            (vwap.iloc[idx - 1], "prev_vwap"),
            (std.iloc[idx - 1], "prev_std"),
        ]:
            if pd.isna(val):
                return self._hold_safe(df, f"Insufficient data for ValueArea ({label} is NaN)")

        curr_close = float(close.iloc[idx])
        prev_close = float(close.iloc[idx - 1])
        curr_vwap = float(vwap.iloc[idx])
        curr_std = float(std.iloc[idx])
        curr_va_high = float(va_high.iloc[idx])
        curr_va_low = float(va_low.iloc[idx])
        prev_va_high = float(va_high.iloc[idx - 1])
        prev_va_low = float(va_low.iloc[idx - 1])

        bull_ctx = f"close={curr_close:.2f} vwap={curr_vwap:.2f} va_low={curr_va_low:.2f}"
        bear_ctx = f"close={curr_close:.2f} vwap={curr_vwap:.2f} va_high={curr_va_high:.2f}"

        # BUY: 이전봉 VA 아래 → 현재봉 VA 재진입
        if prev_close < prev_va_low and curr_close > curr_va_low:
            conf = (
                Confidence.HIGH
                if abs(curr_close - curr_vwap) < curr_std * _HIGH_CONF_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"VA 하단 재진입: prev_close({prev_close:.2f}) < va_low({prev_va_low:.2f}), "
                    f"curr_close({curr_close:.2f}) > va_low({curr_va_low:.2f})"
                ),
                invalidation=f"Close falls below va_low ({curr_va_low:.2f})",
                bull_case=bull_ctx,
                bear_case=bear_ctx,
            )

        # SELL: 이전봉 VA 위 → 현재봉 VA 재진입
        if prev_close > prev_va_high and curr_close < curr_va_high:
            conf = (
                Confidence.HIGH
                if abs(curr_close - curr_vwap) < curr_std * _HIGH_CONF_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"VA 상단 재진입: prev_close({prev_close:.2f}) > va_high({prev_va_high:.2f}), "
                    f"curr_close({curr_close:.2f}) < va_high({curr_va_high:.2f})"
                ),
                invalidation=f"Close rises above va_high ({curr_va_high:.2f})",
                bull_case=bull_ctx,
                bear_case=bear_ctx,
            )

        return self._hold_safe(
            df,
            f"No VA re-entry: close={curr_close:.2f} va_low={curr_va_low:.2f} va_high={curr_va_high:.2f}",
        )

    def _hold_safe(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )
        idx = len(df) - 2
        close = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )
