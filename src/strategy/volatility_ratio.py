"""
VolatilityRatioStrategy: 단기 vs 장기 변동성 비율 기반 전략.
- Short Vol = close의 5기간 표준편차
- Long Vol  = close의 20기간 표준편차
- VR = Short Vol / Long Vol
- BUY:  VR > 1.2 AND close > ema50
- SELL: VR > 1.2 AND close < ema50
- HOLD: VR < 1.2
- confidence: HIGH if VR > 1.5, MEDIUM if VR > 1.2
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_SHORT_PERIOD = 5
_LONG_PERIOD = 20
_VR_SIGNAL = 1.2
_VR_HIGH = 1.5


class VolatilityRatioStrategy(BaseStrategy):
    name = "volatility_ratio"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        short_vol = df["close"].rolling(_SHORT_PERIOD).std()
        long_vol = df["close"].rolling(_LONG_PERIOD).std()
        vr = short_vol / long_vol.replace(0, 1e-10)

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])
        vr_val = float(vr.iloc[idx])

        context = f"close={close:.2f} ema50={ema50:.2f} VR={vr_val:.4f}"

        if vr_val > _VR_SIGNAL:
            confidence = Confidence.HIGH if vr_val > _VR_HIGH else Confidence.MEDIUM
            if close > ema50:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"Volatility Ratio BUY: VR={vr_val:.4f}>{_VR_SIGNAL}, close({close:.2f})>ema50({ema50:.2f})",
                    invalidation=f"VR < {_VR_SIGNAL} or close < ema50({ema50:.2f})",
                    bull_case=context,
                    bear_case=context,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"Volatility Ratio SELL: VR={vr_val:.4f}>{_VR_SIGNAL}, close({close:.2f})<ema50({ema50:.2f})",
                    invalidation=f"VR < {_VR_SIGNAL} or close > ema50({ema50:.2f})",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: VR={vr_val:.4f}<{_VR_SIGNAL}", context, context)

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
