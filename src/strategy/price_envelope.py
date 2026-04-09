"""
Price Envelope 전략:
- Middle = EMA(close, 20)
- Upper = Middle * (1 + 0.02)
- Lower = Middle * (1 - 0.02)
- BUY:  close < Lower (과매도)
- SELL: close > Upper (과매수)
- HOLD: Lower <= close <= Upper
- confidence: HIGH if 이격률 > 3%, MEDIUM if > 2%
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_BAND_PCT = 0.02
_HIGH_CONF_DIST = 3.0
_MED_CONF_DIST = 2.0


class PriceEnvelopeStrategy(BaseStrategy):
    name = "price_envelope"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        band_pct = _BAND_PCT
        ema20 = df["close"].ewm(span=20, adjust=False).mean()
        upper = ema20 * (1 + band_pct)
        lower = ema20 * (1 - band_pct)

        close = float(df["close"].iloc[idx])
        mid = float(ema20.iloc[idx])
        up = float(upper.iloc[idx])
        lo = float(lower.iloc[idx])

        dist_pct = abs(close - mid) / max(abs(mid), 1e-10) * 100

        bull_case = f"close={close:.2f} lower={lo:.2f} upper={up:.2f} mid={mid:.2f} dist={dist_pct:.2f}%"
        bear_case = bull_case

        if close < lo:
            confidence = Confidence.HIGH if dist_pct > _HIGH_CONF_DIST else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"과매도: close({close:.2f}) < lower({lo:.2f}), dist={dist_pct:.2f}%",
                invalidation=f"Close above upper envelope ({up:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if close > up:
            confidence = Confidence.HIGH if dist_pct > _HIGH_CONF_DIST else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"과매수: close({close:.2f}) > upper({up:.2f}), dist={dist_pct:.2f}%",
                invalidation=f"Close below lower envelope ({lo:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"Inside envelope: close={close:.2f} [{lo:.2f}, {up:.2f}]", bull_case, bear_case)

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
