"""
Median Price 전략:
- Median Price (MP) = (high + low) / 2
- MP_EMA = EMA(MP, 20)
- BUY:  MP > MP_EMA AND MP 상승 중 AND close > MP
- SELL: MP < MP_EMA AND MP 하락 중 AND close < MP
- HOLD: 그 외
- confidence: HIGH if |(MP - MP_EMA) / MP_EMA| > 0.01, MEDIUM otherwise
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_SPAN = 20
_HIGH_CONF_RATIO = 0.01


class MedianPriceStrategy(BaseStrategy):
    name = "median_price"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        mp = (df["high"] + df["low"]) / 2
        mp_ema = mp.ewm(span=_EMA_SPAN, adjust=False).mean()

        idx = len(df) - 2
        mp_now = float(mp.iloc[idx])
        mp_prev = float(mp.iloc[idx - 1])
        mp_ema_now = float(mp_ema.iloc[idx])
        close_now = float(df["close"].iloc[idx])

        ratio = (mp_now - mp_ema_now) / (mp_ema_now if mp_ema_now != 0 else 1e-10)
        context = (
            f"close={close_now:.2f} mp={mp_now:.2f} mp_ema={mp_ema_now:.2f} "
            f"mp_prev={mp_prev:.2f} ratio={ratio:.4f}"
        )

        mp_rising = mp_now > mp_prev
        mp_falling = mp_now < mp_prev

        if mp_now > mp_ema_now and mp_rising and close_now > mp_now:
            confidence = Confidence.HIGH if ratio > _HIGH_CONF_RATIO else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MP 상승 추세: mp({mp_now:.2f})>mp_ema({mp_ema_now:.2f}), "
                    f"MP 상승 중, close({close_now:.2f})>mp({mp_now:.2f})"
                ),
                invalidation=f"MP < MP_EMA ({mp_ema_now:.2f}) 또는 MP 하락 전환",
                bull_case=context,
                bear_case=context,
            )

        if mp_now < mp_ema_now and mp_falling and close_now < mp_now:
            confidence = Confidence.HIGH if abs(ratio) > _HIGH_CONF_RATIO else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MP 하락 추세: mp({mp_now:.2f})<mp_ema({mp_ema_now:.2f}), "
                    f"MP 하락 중, close({close_now:.2f})<mp({mp_now:.2f})"
                ),
                invalidation=f"MP > MP_EMA ({mp_ema_now:.2f}) 또는 MP 상승 전환",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: mp={mp_now:.2f} mp_ema={mp_ema_now:.2f}", context, context)

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
