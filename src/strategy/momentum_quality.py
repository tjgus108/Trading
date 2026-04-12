"""
MomentumQuality 전략 (강화 v1.1):
- 모멘텀의 "품질" — 모멘텀이 일관되고 가속되고 있는지 측정.
- BUY: quality_score > 1.0 AND mom20 > 0 AND consistency > 0.4 (추가 필터)
- SELL: quality_score < -0.5 AND mom20 < 0 AND consistency < 0.6 (추가 필터)
- confidence: HIGH if quality_score > 1.5 (BUY) or quality_score < -0.8 (SELL) else MEDIUM
- 최소 행: 25
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class MomentumQualityStrategy(BaseStrategy):
    name = "momentum_quality"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data: {len(df)} < {_MIN_ROWS}")

        idx = len(df) - 2  # _last index

        close = df["close"]

        returns = close.pct_change()
        mom5 = returns.rolling(5).mean()
        mom10 = returns.rolling(10).mean()
        mom20 = returns.rolling(20).mean()
        consistency = (returns > 0).rolling(10).mean()
        acceleration = mom5 - mom10
        quality_score_series = consistency * 2 - 1 + (acceleration > 0).astype(float)

        mom20_val = mom20.iloc[idx]
        quality_score_val = quality_score_series.iloc[idx]
        consistency_val = consistency.iloc[idx]

        # NaN 처리
        if pd.isna(mom20_val) or pd.isna(quality_score_val) or pd.isna(consistency_val):
            return self._hold(df, "Insufficient data: NaN in indicators")

        mom20_val = float(mom20_val)
        quality_score_val = float(quality_score_val)
        consistency_val = float(consistency_val)

        curr_close = float(close.iloc[idx])

        context = (
            f"quality_score={quality_score_val:.3f} mom20={mom20_val:.5f} "
            f"consistency={consistency_val:.2f} curr_close={curr_close:.4f}"
        )

        if quality_score_val > 1.0 and mom20_val > 0 and consistency_val > 0.4:
            conf = Confidence.HIGH if quality_score_val > 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"고품질 상승 모멘텀 (일관성 필터 통과): {context}",
                invalidation="quality_score <= 1.0 또는 mom20 <= 0 또는 consistency <= 0.4",
                bull_case=f"일관되고 가속되는 상승 모멘텀 (score={quality_score_val:.3f}, consistency={consistency_val:.2f})",
                bear_case="모멘텀 품질 하락 또는 일관성 감소 시 빠른 청산",
            )

        if quality_score_val < -0.5 and mom20_val < 0 and consistency_val < 0.6:
            conf = Confidence.HIGH if quality_score_val < -0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"고품질 하락 모멘텀 (일관성 필터 통과): {context}",
                invalidation="quality_score >= -0.5 또는 mom20 >= 0 또는 consistency >= 0.6",
                bull_case="모멘텀 반전 또는 일관성 증가 시 숏 포지션 청산",
                bear_case=f"일관되고 가속되는 하락 모멘텀 (score={quality_score_val:.3f}, consistency={consistency_val:.2f})",
            )

        return self._hold(df, f"모멘텀 품질 신호 없음: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
