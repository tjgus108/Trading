"""
AccelerationBandStrategy: Headley Acceleration Bands 돌파 전략.
- upper = sma20 * (1 + 4 * sma20((high-low)/(high+low)))
- lower = sma20 * (1 - 4 * sma20((high-low)/(high+low)))
- BUY:  close crosses above upper (prev <= upper, now > upper)
- SELL: close crosses below lower (prev >= lower, now < lower)
- confidence: HIGH if close > upper * 1.005 (1% 이상 돌파)
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_HIGH_CONF_MARGIN = 1.005


class AccelerationBandStrategy(BaseStrategy):
    name = "acceleration_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        sma = df["close"].rolling(_PERIOD).mean()
        hl_ratio = (df["high"] - df["low"]) / (df["high"] + df["low"]).replace(0, 1e-10)
        hl_sma = hl_ratio.rolling(_PERIOD).mean()

        upper = sma * (1 + 4 * hl_sma)
        lower = sma * (1 - 4 * hl_sma)

        idx = len(df) - 2
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])
        upper_now = float(upper.iloc[idx])
        upper_prev = float(upper.iloc[idx - 1])
        lower_now = float(lower.iloc[idx])
        lower_prev = float(lower.iloc[idx - 1])

        context = (
            f"close={close_now:.2f} upper={upper_now:.2f} lower={lower_now:.2f}"
        )

        # BUY: close crosses above upper
        if close_prev <= upper_prev and close_now > upper_now:
            confidence = (
                Confidence.HIGH if close_now > upper_now * _HIGH_CONF_MARGIN
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"upper 밴드 상향 돌파: close={close_now:.2f} > upper={upper_now:.2f}",
                invalidation=f"close <= upper={upper_now:.2f}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: close crosses below lower
        if close_prev >= lower_prev and close_now < lower_now:
            confidence = (
                Confidence.HIGH if close_now < lower_now / _HIGH_CONF_MARGIN
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"lower 밴드 하향 돌파: close={close_now:.2f} < lower={lower_now:.2f}",
                invalidation=f"close >= lower={lower_now:.2f}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, "No crossover signal", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        close = float(df["close"].iloc[idx])
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
