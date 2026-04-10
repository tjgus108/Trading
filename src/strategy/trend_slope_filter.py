"""
TrendSlopeFilterStrategy: 선형 회귀 기울기(slope)로 추세 방향·강도 측정.

최근 N봉(기본 20)의 선형 회귀 기울기를 가격 수준으로 정규화하여
양수 가속 시 BUY, 음수 가속 시 SELL.
최소 25행 필요.
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendSlopeFilterStrategy(BaseStrategy):
    name = "trend_slope_filter"

    def __init__(self, window: int = 20, threshold: float = 0.001) -> None:
        self.window = window
        self.threshold = threshold

    def _slope_norm(self, values: np.ndarray) -> float:
        n = len(values)
        x = np.arange(n)
        slope = np.polyfit(x, values, 1)[0]
        mean = values.mean()
        if abs(mean) < 1e-10:
            return 0.0
        return float(slope / mean)

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < 25:
            close_val = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_val,
                reasoning="Insufficient data: minimum 25 rows required.",
                invalidation="",
            )

        idx = len(df) - 2
        n = self.window

        window_curr = df["close"].iloc[idx - n + 1: idx + 1].values
        window_prev = df["close"].iloc[idx - n: idx].values

        if len(window_curr) < n or len(window_prev) < n:
            entry = float(self._last(df)["close"])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data: minimum 25 rows required.",
                invalidation="",
            )

        slope_norm = self._slope_norm(window_curr)
        slope_norm_prev = self._slope_norm(window_prev)

        if slope_norm != slope_norm:  # NaN check
            entry = float(self._last(df)["close"])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in slope calculation.",
                invalidation="",
            )

        th = self.threshold
        conf = Confidence.HIGH if abs(slope_norm) > th * 2 else Confidence.MEDIUM
        entry = float(self._last(df)["close"])

        if slope_norm > th and slope_norm > slope_norm_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"slope_norm={slope_norm:.5f} > threshold={th} and accelerating "
                    f"(prev={slope_norm_prev:.5f}). Uptrend strengthening."
                ),
                invalidation=f"slope_norm이 {th} 아래로 하락 시",
                bull_case=f"slope={slope_norm:.5f} > prev={slope_norm_prev:.5f}",
                bear_case=f"threshold={th}",
            )

        if slope_norm < -th and slope_norm < slope_norm_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"slope_norm={slope_norm:.5f} < -{th} and accelerating downward "
                    f"(prev={slope_norm_prev:.5f}). Downtrend strengthening."
                ),
                invalidation=f"slope_norm이 -{th} 위로 회복 시",
                bull_case=f"threshold={-th}",
                bear_case=f"slope={slope_norm:.5f} < prev={slope_norm_prev:.5f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"slope_norm={slope_norm:.5f} within threshold ±{th}. No clear trend."
            ),
            invalidation="",
            bull_case=f"slope_norm={slope_norm:.5f}",
            bear_case=f"slope_norm={slope_norm:.5f}",
        )
