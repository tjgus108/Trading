"""
MomentumAccelerationStrategy: 모멘텀 가속도 기반 추세 강화 감지.

로직:
  - mom5  = close.pct_change(5) * 100
  - mom10 = close.pct_change(10) * 100
  - accel = mom5 - mom10 / 2  (단기 모멘텀이 장기보다 강할수록 가속)
  - accel_ema = accel.ewm(span=5).mean()
  - BUY:  accel_ema > 0.5 AND mom5 > 0 AND close > EMA20
  - SELL: accel_ema < -0.5 AND mom5 < 0 AND close < EMA20
  - confidence HIGH: |accel_ema| > 1.5
  - 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class MomentumAccelerationStrategy(BaseStrategy):
    name = "momentum_accel"

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

        mom5 = close.pct_change(5) * 100
        mom10 = close.pct_change(10) * 100
        accel = mom5 - mom10 / 2
        accel_ema = accel.ewm(span=5, adjust=False).mean()

        accel_ema_val = float(accel_ema.iloc[idx])
        mom5_val = float(mom5.iloc[idx])

        entry = float(close.iloc[idx])

        # EMA20: 컬럼이 있으면 사용, 없으면 계산
        if "ema20" in df.columns:
            ema20 = float(df["ema20"].iloc[idx])
        else:
            ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[idx])

        context = (
            f"close={entry:.4f} ema20={ema20:.4f} "
            f"mom5={mom5_val:.4f} accel_ema={accel_ema_val:.4f}"
        )

        if accel_ema_val > 0.5 and mom5_val > 0 and entry > ema20:
            confidence = Confidence.HIGH if accel_ema_val > 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Momentum Acceleration BUY: accel_ema={accel_ema_val:.4f}>0.5, "
                    f"mom5={mom5_val:.4f}>0, close({entry:.4f})>ema20({ema20:.4f})"
                ),
                invalidation=f"accel_ema < 0 또는 close < ema20({ema20:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if accel_ema_val < -0.5 and mom5_val < 0 and entry < ema20:
            confidence = Confidence.HIGH if accel_ema_val < -1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Momentum Acceleration SELL: accel_ema={accel_ema_val:.4f}<-0.5, "
                    f"mom5={mom5_val:.4f}<0, close({entry:.4f})<ema20({ema20:.4f})"
                ),
                invalidation=f"accel_ema > 0 또는 close > ema20({ema20:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Momentum Acceleration HOLD: accel_ema={accel_ema_val:.4f} "
                f"mom5={mom5_val:.4f} close_vs_ema20={'above' if entry > ema20 else 'below'}"
            ),
            invalidation="",
            bull_case=context,
            bear_case=context,
        )
