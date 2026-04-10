"""
VolatilitySurfaceStrategy: 단기/장기 실현 변동성 비율 기반 (volatility term structure).
- BUY:  vol_ratio < 0.8 AND close > close_ma20 AND vol_ratio < vol_ratio_ma
- SELL: vol_ratio < 0.8 AND close < close_ma20 AND vol_ratio < vol_ratio_ma
- confidence: HIGH if vol_ratio < 0.6 else MEDIUM
- 최소 데이터: 30행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class VolatilitySurfaceStrategy(BaseStrategy):
    name = "volatility_surface"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        rv_short = close.pct_change().rolling(5, min_periods=1).std() * 100
        rv_long = close.pct_change().rolling(20, min_periods=1).std() * 100
        vol_ratio = rv_short / (rv_long + 1e-10)
        vol_ratio_ma = vol_ratio.rolling(10, min_periods=1).mean()
        close_ma20 = close.ewm(span=20, adjust=False).mean()

        idx = len(df) - 2

        vr_val = float(vol_ratio.iloc[idx])
        vrma_val = float(vol_ratio_ma.iloc[idx])
        close_val = float(close.iloc[idx])
        ma20_val = float(close_ma20.iloc[idx])

        if any(np.isnan(v) for v in [vr_val, vrma_val, close_val, ma20_val]):
            return self._hold(df, "NaN in indicators")

        context = (
            f"vol_ratio={vr_val:.3f} vol_ratio_ma={vrma_val:.3f} "
            f"close={close_val:.2f} close_ma20={ma20_val:.2f}"
        )

        if vr_val < 0.8 and vr_val < vrma_val:
            confidence = Confidence.HIGH if vr_val < 0.6 else Confidence.MEDIUM
            if close_val > ma20_val:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_val,
                    reasoning=f"변동성 수렴 + 상승추세: vol_ratio={vr_val:.3f}<0.8, close={close_val:.2f}>ma20={ma20_val:.2f}",
                    invalidation=f"vol_ratio > 0.8 or close < ma20",
                    bull_case=context,
                    bear_case=context,
                )
            elif close_val < ma20_val:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_val,
                    reasoning=f"변동성 수렴 + 하락추세: vol_ratio={vr_val:.3f}<0.8, close={close_val:.2f}<ma20={ma20_val:.2f}",
                    invalidation=f"vol_ratio > 0.8 or close > ma20",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: vol_ratio={vr_val:.3f}", context, context)

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
