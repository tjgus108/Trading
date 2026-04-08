"""
VWAP Reversion 전략 (약세장용):
- BUY: close < vwap * 0.995 AND rsi14 < 35 (VWAP 하방 이탈 + 과매도)
- SELL: close > vwap * 1.005 AND rsi14 > 65 (VWAP 상방 이탈 + 과매수)
- HOLD: 그 외
- 최소 데이터: 50행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 50
_VWAP_LOWER_BAND = 0.995
_VWAP_UPPER_BAND = 1.005
_RSI_OVERSOLD = 35
_RSI_OVERBOUGHT = 65
_RSI_EXTREME_OVERSOLD = 25
_RSI_EXTREME_OVERBOUGHT = 75


class VWAPReversionStrategy(BaseStrategy):
    name = "vwap_reversion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        vwap = float(last["vwap"])
        rsi = float(last["rsi14"])

        below_vwap = close < vwap * _VWAP_LOWER_BAND
        above_vwap = close > vwap * _VWAP_UPPER_BAND
        oversold = rsi < _RSI_OVERSOLD
        overbought = rsi > _RSI_OVERBOUGHT

        bull_case = f"close={close:.2f} vwap={vwap:.2f} rsi={rsi:.1f} (below vwap*{_VWAP_LOWER_BAND}={vwap*_VWAP_LOWER_BAND:.2f})"
        bear_case = f"close={close:.2f} vwap={vwap:.2f} rsi={rsi:.1f} (above vwap*{_VWAP_UPPER_BAND}={vwap*_VWAP_UPPER_BAND:.2f})"

        if below_vwap and oversold:
            confidence = Confidence.HIGH if rsi < _RSI_EXTREME_OVERSOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"VWAP 하방 이탈 + 과매도: close({close:.2f}) < vwap*{_VWAP_LOWER_BAND}({vwap*_VWAP_LOWER_BAND:.2f}), rsi={rsi:.1f}",
                invalidation=f"Close above VWAP ({vwap:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if above_vwap and overbought:
            confidence = Confidence.HIGH if rsi > _RSI_EXTREME_OVERBOUGHT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"VWAP 상방 이탈 + 과매수: close({close:.2f}) > vwap*{_VWAP_UPPER_BAND}({vwap*_VWAP_UPPER_BAND:.2f}), rsi={rsi:.1f}",
                invalidation=f"Close below VWAP ({vwap:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"No signal: close={close:.2f} vwap={vwap:.2f} rsi={rsi:.1f}", bull_case, bear_case)

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
