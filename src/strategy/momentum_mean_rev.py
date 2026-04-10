"""
MomentumMeanRevStrategy: 모멘텀 + 평균 회귀 혼합.
추세 방향의 풀백(Z-score 기반) 진입.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class MomentumMeanRevStrategy(BaseStrategy):
    name = "momentum_mean_rev"

    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: minimum {self.MIN_ROWS} rows required",
                invalidation="",
            )

        close = df["close"]

        mom10 = close.pct_change(10)
        mom10_ma = mom10.rolling(5, min_periods=1).mean()

        roll_mean = close.rolling(20, min_periods=1).mean()
        roll_std = close.rolling(20, min_periods=1).std()
        z_price = (close - roll_mean) / (roll_std + 1e-10)

        mom10_std = mom10.rolling(20, min_periods=1).std()

        idx = len(df) - 2
        last = df.iloc[idx]

        c = close.iloc[idx]
        mm = mom10_ma.iloc[idx]
        z = z_price.iloc[idx]
        ms = mom10_std.iloc[idx]

        # NaN 체크
        if any(v is None or (isinstance(v, float) and np.isnan(v))
               for v in [c, mm, z]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=float(c) if c and not np.isnan(c) else 0.0,
                reasoning="NaN values detected in indicators",
                invalidation="",
            )

        entry = float(c)

        buy_signal = (mm > 0) and (z < -0.5) and (z > -2.0)
        sell_signal = (mm < 0) and (z > 0.5) and (z < 2.0)

        ms_val = float(ms) if ms is not None and not np.isnan(ms) else 0.0
        mm_abs = abs(float(mm))
        z_abs = abs(float(z))

        high_conf = (z_abs > 1.0) and (mm_abs > ms_val)

        if buy_signal:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Momentum pullback buy: mom10_ma={mm:.4f}>0, "
                    f"z_price={z:.4f} in (-2, -0.5)"
                ),
                invalidation=f"Z-score drops below -2.0 or mom10_ma turns negative",
                bull_case=f"Upward momentum with mean-reversion pullback entry",
                bear_case=f"Momentum could fade; z_price={z:.4f}",
            )

        if sell_signal:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Momentum pullback sell: mom10_ma={mm:.4f}<0, "
                    f"z_price={z:.4f} in (0.5, 2)"
                ),
                invalidation=f"Z-score rises above 2.0 or mom10_ma turns positive",
                bull_case=f"Momentum could reverse; z_price={z:.4f}",
                bear_case=f"Downward momentum with mean-reversion bounce entry",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No signal: mom10_ma={mm:.4f}, z_price={z:.4f}. "
                f"BUY needs mom>0 & -2<z<-0.5; SELL needs mom<0 & 0.5<z<2"
            ),
            invalidation="",
            bull_case=f"mom10_ma={mm:.4f} z_price={z:.4f}",
            bear_case=f"mom10_ma={mm:.4f} z_price={z:.4f}",
        )
