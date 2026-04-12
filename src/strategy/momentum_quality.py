"""
MomentumQuality 전략 (강화 v1.1):
- 모멘텀의 "품질" — 모멘텀이 일관되고 가속되고 있는지 측정.
- BUY: quality_score > 1.0 AND mom20 > 0 AND RSI < 70 (과매수 필터)
- SELL: quality_score < -0.5 AND mom20 < 0 AND RSI > 30 (과매도 필터)
- confidence: HIGH if quality_score > 1.5 (BUY) or quality_score < -0.8 (SELL) else MEDIUM
- 최소 행: 25
"""

from typing import Optional

import pandas as pd
import numpy as np

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

        # RSI 14 계산
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi14 = 100 - (100 / (1 + rs))
        rsi_val = rsi14.iloc[idx]

        # NaN 처리
        if pd.isna(mom20_val) or pd.isna(quality_score_val) or pd.isna(rsi_val):
            return self._hold(df, "Insufficient data: NaN in indicators")

        mom20_val = float(mom20_val)
        quality_score_val = float(quality_score_val)
        rsi_val = float(rsi_val)

        curr_close = float(close.iloc[idx])

        context = (
            f"quality_score={quality_score_val:.3f} mom20={mom20_val:.5f} "
            f"rsi14={rsi_val:.1f} curr_close={curr_close:.4f}"
        )

        if quality_score_val > 1.0 and mom20_val > 0 and rsi_val < 70:
            conf = Confidence.HIGH if quality_score_val > 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"고품질 상승 모멘텀 (RSI 필터 통과): {context}",
                invalidation="quality_score <= 1.0 또는 mom20 <= 0 또는 RSI >= 70",
                bull_case=f"일관되고 가속되는 상승 모멘텀, RSI 미과매수 (score={quality_score_val:.3f})",
                bear_case="모멘텀 품질 하락 또는 RSI 상승 시 빠른 청산",
            )

        if quality_score_val < -0.5 and mom20_val < 0 and rsi_val > 30:
            conf = Confidence.HIGH if quality_score_val < -0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"고품질 하락 모멘텀 (RSI 필터 통과): {context}",
                invalidation="quality_score >= -0.5 또는 mom20 >= 0 또는 RSI <= 30",
                bull_case="모멘텀 반전 또는 RSI 하락 시 숏 포지션 청산",
                bear_case=f"일관되고 가속되는 하락 모멘텀, RSI 미과매도 (score={quality_score_val:.3f})",
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
