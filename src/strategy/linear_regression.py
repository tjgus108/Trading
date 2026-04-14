"""
Linear Regression Slope 전략:
- 최근 20봉에 선형 회귀 적용
  - Slope: 기울기 (가격 변화율)
  - R²: 결정계수 (추세 신뢰도)
  - Predicted: 회귀선의 현재(마지막) 예측값
- BUY:  Slope > 0 AND R² > 0.7 AND close > Predicted
- SELL: Slope < 0 AND R² > 0.7 AND close < Predicted
- HOLD: R² < 0.7 (추세 불명확)
- confidence: HIGH if R² > 0.9, MEDIUM if R² > 0.7
- 최소 25행 필요, idx = len(df) - 2
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_R2_MEDIUM = 0.7
_R2_HIGH = 0.9


def _linear_regression(y: np.ndarray) -> Tuple[float, float, float]:
    """기울기, 마지막 예측값, R² 반환."""
    period = len(y)
    x = np.arange(period)
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    predicted = float(np.polyval(coeffs, period - 1))
    y_mean = y.mean()
    ss_res = ((y - np.polyval(coeffs, x)) ** 2).sum()
    ss_tot = ((y - y_mean) ** 2).sum()
    r_squared = float(1 - ss_res / (ss_tot + 1e-10))
    return slope, predicted, r_squared


class LinearRegressionStrategy(BaseStrategy):
    """선형 회귀 기울기 기반 추세 추종 전략."""

    name = "linear_regression"

    def __init__(self, period: int = _PERIOD):
        self.period = period

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
            )

        idx = len(df) - 2
        y = df["close"].iloc[idx - self.period + 1: idx + 1].values

        if len(y) < self.period:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[idx]),
                reasoning="회귀 구간 데이터 부족",
                invalidation="데이터 충분 시 재평가",
            )

        slope, predicted, r_squared = _linear_regression(y)
        close = float(df["close"].iloc[idx])

        # 추세 불명확
        if r_squared < _R2_MEDIUM:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"R²={r_squared:.3f} < {_R2_MEDIUM} — 추세 불명확 "
                    f"(slope={slope:.4f}, predicted={predicted:.2f})"
                ),
                invalidation=f"R² > {_R2_MEDIUM} 확인 후 재평가",
            )

        # Confidence 결정
        if r_squared > _R2_HIGH:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        # BUY
        if slope > 0 and close > predicted:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"상승 추세: slope={slope:.4f} > 0, "
                    f"R²={r_squared:.3f}, close={close:.2f} > predicted={predicted:.2f}"
                ),
                invalidation="Slope 음전환 또는 R² < 0.7 시 무효",
                bull_case="강한 선형 상승 추세 지속 기대",
                bear_case="추세 약화 시 반전 가능",
            )

        # SELL
        if slope < 0 and close < predicted:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"하락 추세: slope={slope:.4f} < 0, "
                    f"R²={r_squared:.3f}, close={close:.2f} < predicted={predicted:.2f}"
                ),
                invalidation="Slope 양전환 또는 R² < 0.7 시 무효",
                bull_case="추세 반전 시 반등 가능",
                bear_case="강한 선형 하락 추세 지속 기대",
            )

        # slope와 close 방향 불일치 → HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"조건 불일치: slope={slope:.4f}, "
                f"close={close:.2f}, predicted={predicted:.2f}, R²={r_squared:.3f}"
            ),
            invalidation="close와 predicted 방향 일치 시 재평가",
        )
