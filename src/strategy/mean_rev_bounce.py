"""
MeanRevBounceStrategy:
- Z-score 기반 강한 평균 회귀 후 반등/반락 신호
- BUY:  z_score < -1.5 AND z_change > 0 (과매도 후 z-score 반등)
- SELL: z_score > 1.5  AND z_change < 0 (과매수 후 z-score 반락)
- confidence: HIGH(abs(z_score) > 2.0), MEDIUM 그 외
- 최소 데이터: 20행
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_Z_THRESHOLD = 1.5
_Z_HIGH_CONF = 2.0
_EPS = 1e-10


class MeanRevBounceStrategy(BaseStrategy):
    name = "mean_rev_bounce"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # 마지막 완성 캔들

        close = df["close"]

        ma20 = close.rolling(20, min_periods=1).mean()
        std20 = close.rolling(20, min_periods=1).std()
        z_score = (close - ma20) / (std20 + _EPS)
        z_prev = z_score.shift(1)
        z_change = z_score - z_prev

        z_val = z_score.iloc[idx]
        z_change_val = z_change.iloc[idx]
        close_val = float(close.iloc[idx])

        # NaN 체크
        if _isnan(z_val) or _isnan(z_change_val):
            return self._hold(df, "NaN in z_score")

        z_val = float(z_val)
        z_change_val = float(z_change_val)

        confidence = Confidence.HIGH if abs(z_val) > _Z_HIGH_CONF else Confidence.MEDIUM

        context = (
            f"z_score={z_val:.4f} z_change={z_change_val:.4f} close={close_val:.4f}"
        )

        if z_val < -_Z_THRESHOLD and z_change_val > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"과매도 반등: z_score({z_val:.4f})<-{_Z_THRESHOLD}, "
                    f"z_change({z_change_val:.4f})>0"
                ),
                invalidation=f"z_score continues below -{_Z_THRESHOLD} without recovery",
                bull_case=context,
                bear_case=context,
            )

        if z_val > _Z_THRESHOLD and z_change_val < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"과매수 반락: z_score({z_val:.4f})>{_Z_THRESHOLD}, "
                    f"z_change({z_change_val:.4f})<0"
                ),
                invalidation=f"z_score continues above {_Z_THRESHOLD} without reversal",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No mean-rev signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2
        close_val = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )


def _isnan(v) -> bool:
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return True
