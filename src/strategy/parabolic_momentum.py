"""
ParabolicMomentumStrategy: 가격 가속도 기반 포물선 모멘텀.

로직:
  - returns = close.pct_change()
  - accel = returns.diff()  # 2차 미분 (가속도)
  - accel_ma = accel.rolling(10, min_periods=1).mean()
  - accel_std = accel.rolling(20, min_periods=1).std()
  - BUY: accel > accel_ma AND accel > 0 AND accel > accel_std * 0.5
  - SELL: accel < accel_ma AND accel < 0 AND accel < -accel_std * 0.5
  - confidence HIGH: abs(accel) > accel_std * 1.5 else MEDIUM
  - 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class ParabolicMomentumStrategy(BaseStrategy):
    name = "parabolic_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
            )

        idx = len(df) - 2  # 마지막 완성봉
        close = df["close"]

        returns = close.pct_change()
        accel = returns.diff()
        accel_ma = accel.rolling(10, min_periods=1).mean()
        accel_std = accel.rolling(20, min_periods=1).std().fillna(0.0)

        accel_val = float(accel.iloc[idx])
        accel_ma_val = float(accel_ma.iloc[idx])
        accel_std_val = float(accel_std.iloc[idx])
        entry = float(close.iloc[idx])

        context = (
            f"close={entry:.4f} accel={accel_val:.6f} "
            f"accel_ma={accel_ma_val:.6f} accel_std={accel_std_val:.6f}"
        )

        if (
            accel_val > accel_ma_val
            and accel_val > 0
            and accel_val > accel_std_val * 0.5
        ):
            confidence = (
                Confidence.HIGH
                if abs(accel_val) > accel_std_val * 1.5
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Parabolic Momentum BUY: accel={accel_val:.6f}>accel_ma={accel_ma_val:.6f}, "
                    f"accel>0, accel>{accel_std_val * 0.5:.6f} (accel_std*0.5)"
                ),
                invalidation=f"accel < accel_ma 또는 accel < 0",
                bull_case=context,
                bear_case=context,
            )

        if (
            accel_val < accel_ma_val
            and accel_val < 0
            and accel_val < -accel_std_val * 0.5
        ):
            confidence = (
                Confidence.HIGH
                if abs(accel_val) > accel_std_val * 1.5
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Parabolic Momentum SELL: accel={accel_val:.6f}<accel_ma={accel_ma_val:.6f}, "
                    f"accel<0, accel<-{accel_std_val * 0.5:.6f} (accel_std*0.5)"
                ),
                invalidation=f"accel > accel_ma 또는 accel > 0",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Parabolic Momentum HOLD: accel={accel_val:.6f} "
                f"accel_ma={accel_ma_val:.6f} 조건 미충족"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
