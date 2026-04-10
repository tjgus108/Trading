"""
VelocityEntryStrategy:
- BUY:  velocity > velocity_ma AND acceleration > 0 (속도 평균 초과 + 가속)
- SELL: velocity < velocity_ma AND acceleration < 0 (속도 평균 미달 + 감속)
- HOLD: 그 외
- confidence: HIGH if velocity > velocity.rolling(20).std() else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class VelocityEntryStrategy(BaseStrategy):
    name = "velocity_entry"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for velocity_entry (need 20 rows)")

        close = df["close"]
        velocity = close.diff()
        velocity_ma = velocity.rolling(10).mean()
        acceleration = velocity.diff()
        velocity_std = velocity.rolling(20).std()

        idx = len(df) - 2

        v = velocity.iloc[idx]
        v_ma = velocity_ma.iloc[idx]
        acc = acceleration.iloc[idx]
        v_std = velocity_std.iloc[idx]

        # NaN check
        if pd.isna(v) or pd.isna(v_ma) or pd.isna(acc) or pd.isna(v_std):
            return self._hold(df, "Insufficient data for velocity_entry (NaN in indicators)")

        entry_price = float(close.iloc[idx])
        context = f"velocity={v:.4f} velocity_ma={v_ma:.4f} acceleration={acc:.4f} vel_std={v_std:.4f}"

        confidence = Confidence.HIGH if abs(v) > v_std else Confidence.MEDIUM

        if v > v_ma and acc > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"속도 평균 초과 + 가속: velocity={v:.4f}>{v_ma:.4f}, acceleration={acc:.4f}>0",
                invalidation=f"velocity < velocity_ma or acceleration < 0",
                bull_case=context,
                bear_case=context,
            )

        if v < v_ma and acc < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"속도 평균 미달 + 감속: velocity={v:.4f}<{v_ma:.4f}, acceleration={acc:.4f}<0",
                invalidation=f"velocity > velocity_ma or acceleration > 0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: velocity={v:.4f} v_ma={v_ma:.4f} acc={acc:.4f}", context, context)

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
