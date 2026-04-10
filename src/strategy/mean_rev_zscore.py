"""
MeanRevZScoreStrategy: Z-Score 기반 평균회귀 전략.
- BUY:  zscore < -2.0 AND zscore > zscore.shift(1) (과매도 + 회복 시작)
- SELL: zscore > 2.0  AND zscore < zscore.shift(1) (과매수 + 하락 시작)
- HOLD: -2.0 <= zscore <= 2.0
- confidence: HIGH if abs(zscore) > 2.5 else MEDIUM
- 최소 데이터: 30행
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_BUY_THRESHOLD = -2.0
_SELL_THRESHOLD = 2.0
_HIGH_CONF_ABS = 2.5


class MeanRevZScoreStrategy(BaseStrategy):
    name = "mean_rev_zscore"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for mean_rev_zscore (need 30 rows)")

        close = df["close"]
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std().replace(0, 1e-10)
        zscore = (close - sma20) / std20
        zscore_ma = zscore.rolling(5).mean()  # 단기 평활 (필요 시 활용)  # noqa: F841

        idx = len(df) - 2
        z_now = float(zscore.iloc[idx])
        z_prev = float(zscore.iloc[idx - 1]) if idx >= 1 else z_now
        close_now = float(close.iloc[idx])

        if math.isnan(z_now) or math.isnan(z_prev):
            return self._hold(df, "Insufficient data for mean_rev_zscore (NaN in zscore)")

        context = f"close={close_now:.2f} zscore={z_now:.4f}"

        # BUY: 과매도 + 회복 시작
        if z_now < _BUY_THRESHOLD and z_now > z_prev:
            confidence = Confidence.HIGH if abs(z_now) > _HIGH_CONF_ABS else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"zscore 과매도 회복: z={z_now:.4f}<{_BUY_THRESHOLD} and rising",
                invalidation=f"zscore >= {_BUY_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 과매수 + 하락 시작
        if z_now > _SELL_THRESHOLD and z_now < z_prev:
            confidence = Confidence.HIGH if abs(z_now) > _HIGH_CONF_ABS else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"zscore 과매수 하락: z={z_now:.4f}>{_SELL_THRESHOLD} and falling",
                invalidation=f"zscore <= {_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: zscore={z_now:.4f}", context, context)

    def _hold(self, df: Optional[pd.DataFrame], reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) == 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        idx = len(df) - 2 if len(df) >= 2 else 0
        close = float(df["close"].iloc[idx])
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
