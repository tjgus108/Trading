"""
TrendQualityStrategy: R² + slope 크기 + 가속도 결합 추세 품질 전략.

- Quality score = r_squared * abs(normalized_slope)
  (normalized_slope = slope / mean_price, 20봉 창)
- BUY:  r_squared > 0.8 AND slope > 0 AND quality_score > 0.05
- SELL: r_squared > 0.8 AND slope < 0 AND quality_score > 0.05
- confidence: HIGH if r_squared > 0.9 AND quality_score > 0.09
- 최소 행: 25

참고: normalized_slope = slope/mean_price 기준으로 20봉 선형 추세의
      이론적 최대 quality_score ≈ 0.105 (d/mean 상한).
      따라서 임계값은 0.05(신호) / 0.09(HIGH) 사용.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
PERIOD = 20


class TrendQualityStrategy(BaseStrategy):
    name = "trend_quality"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: 추세 품질 계산 불가",
                invalidation="",
            )

        idx = len(df) - 2
        y = df["close"].iloc[idx - PERIOD + 1: idx + 1].values.astype(float)
        x = np.arange(PERIOD, dtype=float)

        coeffs = np.polyfit(x, y, 1)
        slope = float(coeffs[0])
        fitted = np.polyval(coeffs, x)

        ss_res = float(np.sum((y - fitted) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r_squared = 1.0 - ss_res / max(ss_tot, 1e-10)

        # normalized slope: slope / mean_price
        mean_price = float(y.mean())
        normalized_slope = slope / max(mean_price, 1e-10)
        quality_score = r_squared * abs(normalized_slope)

        close = float(df["close"].iloc[idx])

        info = (
            f"R²={r_squared:.3f}, slope={slope:.4f}, "
            f"quality={quality_score:.4f}"
        )

        if r_squared <= 0.8 or quality_score <= 0.05:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=f"추세 품질 기준 미달. {info}",
                invalidation="R²>0.8 AND quality_score>0.05 충족 시 재평가",
                bull_case=info,
                bear_case=info,
            )

        # confidence 결정
        if r_squared > 0.9 and quality_score > 0.09:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        if slope > 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"상승 추세 품질 우수. {info}",
                invalidation="R²<0.8 또는 quality_score<0.05 또는 slope<0",
                bull_case=info,
                bear_case=info,
            )

        # slope < 0
        return Signal(
            action=Action.SELL,
            confidence=conf,
            strategy=self.name,
            entry_price=close,
            reasoning=f"하락 추세 품질 우수. {info}",
            invalidation="R²<0.8 또는 quality_score<0.05 또는 slope>0",
            bull_case=info,
            bear_case=info,
        )
