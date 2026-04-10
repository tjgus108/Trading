"""
CyclicMomentumStrategy:
- 가격 사이클 감지 + 모멘텀 결합
- BUY:  z_cycle < -1.0 AND z_cycle > z_cycle.shift(1) AND roc5 > 0
- SELL: z_cycle > 1.0  AND z_cycle < z_cycle.shift(1) AND roc5 < 0
- confidence: HIGH if abs(z_cycle) > 1.5 else MEDIUM
- 최소 데이터: 30행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class CyclicMomentumStrategy(BaseStrategy):
    name = "cyclic_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        detrended = close - close.rolling(20, min_periods=1).mean()
        cycle_osc = detrended.rolling(5, min_periods=1).mean()
        cycle_std = detrended.rolling(20, min_periods=1).std()
        z_cycle = cycle_osc / (cycle_std + 1e-10)
        roc5 = close.pct_change(5)

        idx = len(df) - 2
        z_now = z_cycle.iloc[idx]
        z_prev = z_cycle.iloc[idx - 1]
        roc_now = roc5.iloc[idx]

        if any(v != v for v in [z_now, z_prev, roc_now]):  # NaN check
            return self._hold(df, "NaN in indicators")

        last = self._last(df)
        entry = float(last["close"])
        context = f"z_cycle={z_now:.3f} z_prev={z_prev:.3f} roc5={roc_now:.4f}"

        if z_now < -1.0 and z_now > z_prev and roc_now > 0:
            confidence = Confidence.HIGH if abs(z_now) > 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"사이클 저점 반등: {context}",
                invalidation=f"z_cycle >= -1.0 or roc5 <= 0",
                bull_case=context,
                bear_case=context,
            )

        if z_now > 1.0 and z_now < z_prev and roc_now < 0:
            confidence = Confidence.HIGH if abs(z_now) > 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"사이클 고점 하락: {context}",
                invalidation=f"z_cycle <= 1.0 or roc5 >= 0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df) if len(df) >= 2 else df.iloc[-1]
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
