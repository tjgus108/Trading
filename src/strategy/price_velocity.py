"""
Price Velocity 전략 (가격 속도 + 가속도):
- velocity  = (close - close.shift(5)) / 5
- accel     = velocity - velocity.shift(5)
- vol_vel   = EWM(close.pct_change().rolling(10).std(), span=5)  — 정규화용 변동성

- BUY:  velocity > 0 AND accel > 0 AND velocity > vol_vel * 0.5
- SELL: velocity < 0 AND accel < 0 AND abs(velocity) > vol_vel * 0.5
- HOLD: 그 외
- confidence: HIGH if |velocity| > vol_vel * 1.0, MEDIUM 그 외
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class PriceVelocityStrategy(BaseStrategy):
    name = "price_velocity"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        velocity_series = (close - close.shift(5)) / 5
        accel_series = velocity_series - velocity_series.shift(5)
        vol_vel_series = (
            close.pct_change().rolling(10).std().ewm(span=5, adjust=False).mean()
        )

        # 신호 봉 = iloc[-2]
        vel = float(velocity_series.iloc[-2])
        acc = float(accel_series.iloc[-2])
        vv = float(vol_vel_series.iloc[-2])
        entry_price = float(close.iloc[-2])

        # NaN 방어
        if pd.isna(vel) or pd.isna(acc) or pd.isna(vv) or vv == 0:
            return self._hold(df, "Indicator NaN or zero vol_velocity")

        abs_vel = abs(vel)
        threshold_entry = vv * 0.5
        threshold_high = vv * 1.0

        info = (
            f"velocity={vel:.6f} accel={acc:.6f} "
            f"vol_vel={vv:.6f} threshold={threshold_entry:.6f}"
        )

        if vel > 0 and acc > 0 and vel > threshold_entry:
            confidence = Confidence.HIGH if abs_vel > threshold_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"Price velocity 상승 가속: {info}",
                invalidation="velocity 음전환 또는 가속도 음전환",
                bull_case=info,
                bear_case=info,
            )

        if vel < 0 and acc < 0 and abs_vel > threshold_entry:
            confidence = Confidence.HIGH if abs_vel > threshold_high else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"Price velocity 하락 가속: {info}",
                invalidation="velocity 양전환 또는 가속도 양전환",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

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
