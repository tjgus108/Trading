"""
PriceVelocityFilterStrategy: EMA 기반 가격 속도 + 가속도 필터로 추세 강도 판단.

- vel = EMA(5) - EMA(20)
- vel_ma = vel.rolling(10).mean()
- accel = vel.diff(3)  — 3봉 속도 변화

- BUY:  vel > 0 AND vel > vel_ma AND accel > 0
- SELL: vel < 0 AND vel < vel_ma AND accel < 0
- confidence: HIGH if |vel| > vel.rolling(20).std() else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class PriceVelocityFilterStrategy(BaseStrategy):
    name = "price_velocity_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        vel_series = (
            close.ewm(span=5, adjust=False).mean()
            - close.ewm(span=20, adjust=False).mean()
        )
        vel_ma_series = vel_series.rolling(10, min_periods=1).mean()
        accel_series = vel_series.diff(3)
        vel_std_series = vel_series.rolling(20, min_periods=1).std()

        idx = len(df) - 2
        vel = float(vel_series.iloc[idx])
        vel_ma = float(vel_ma_series.iloc[idx])
        accel = float(accel_series.iloc[idx])
        vel_std = float(vel_std_series.iloc[idx])
        entry_price = float(close.iloc[idx])

        if pd.isna(vel) or pd.isna(vel_ma) or pd.isna(accel):
            return self._hold(df, "Indicator NaN")

        info = (
            f"vel={vel:.6f} vel_ma={vel_ma:.6f} "
            f"accel={accel:.6f} vel_std={vel_std:.6f}"
        )

        vel_std_safe = vel_std if not pd.isna(vel_std) and vel_std > 0 else None

        if vel > 0 and vel > vel_ma and accel > 0:
            confidence = (
                Confidence.HIGH
                if vel_std_safe is not None and abs(vel) > vel_std_safe
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"가격 속도 상승 + 가속: {info}",
                invalidation="vel 음전환 또는 가속도 음전환",
                bull_case=info,
                bear_case=info,
            )

        if vel < 0 and vel < vel_ma and accel < 0:
            confidence = (
                Confidence.HIGH
                if vel_std_safe is not None and abs(vel) > vel_std_safe
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"가격 속도 하락 + 가속: {info}",
                invalidation="vel 양전환 또는 가속도 양전환",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
