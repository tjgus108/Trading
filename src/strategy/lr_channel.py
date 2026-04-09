"""
Linear Regression Channel 전략:
- period = 20
- numpy만으로 slope/intercept 직접 계산
- lr_center = intercept + slope * (period-1)
- upper/lower channel = lr_center ± 2 * std(residuals, period)
- BUY:  close < lower_channel AND slope > 0
- SELL: close > upper_channel AND slope < 0
- confidence: HIGH if |residual| > 2.5 * std, MEDIUM if > 2.0
- 최소 데이터: 30행
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_PERIOD = 20


def _calc_lr(close_window: np.ndarray) -> Tuple[float, float]:
    """slope, intercept 반환 (numpy 직접 계산)."""
    period = len(close_window)
    x = np.arange(period, dtype=float)
    x_mean = (period - 1) / 2.0
    y_mean = close_window.mean()
    numerator = float(np.sum((x - x_mean) * (close_window - y_mean)))
    denominator = float(np.sum((x - x_mean) ** 2))
    slope = numerator / denominator if denominator != 0.0 else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


class LRChannelStrategy(BaseStrategy):
    """선형 회귀 채널 기반 역추세 전략."""

    name = "lr_channel"

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
        close_series = df["close"]
        close = float(close_series.iloc[idx])

        # 최근 period 구간으로 slope/intercept 계산
        window = close_series.iloc[idx - self.period + 1: idx + 1].values.astype(float)
        slope, intercept = _calc_lr(window)
        lr_center = intercept + slope * (self.period - 1)

        # residuals: 각 봉의 실제값 - 해당 시점의 lr 예측값
        x_arr = np.arange(self.period, dtype=float)
        lr_line = intercept + slope * x_arr
        residuals = window - lr_line
        std_res = float(np.std(residuals, ddof=0)) if len(residuals) > 1 else 0.0

        upper_channel = lr_center + 2.0 * std_res
        lower_channel = lr_center - 2.0 * std_res

        # 현재 잔차
        current_residual = close - lr_center
        abs_residual = abs(current_residual)

        # confidence
        if std_res > 0 and abs_residual > 2.5 * std_res:
            confidence = Confidence.HIGH
        elif std_res > 0 and abs_residual > 2.0 * std_res:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        context = (
            f"close={close:.2f} lr_center={lr_center:.2f} "
            f"upper={upper_channel:.2f} lower={lower_channel:.2f} "
            f"slope={slope:.6f} std_res={std_res:.4f}"
        )

        # BUY: 하락 채널에서 상승 추세
        if close < lower_channel and slope > 0:
            if confidence == Confidence.LOW:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"채널 하단 돌파 + 상승 추세: "
                    f"close={close:.2f} < lower={lower_channel:.2f}, slope={slope:.6f} > 0"
                ),
                invalidation=f"close < lower_channel 해소 또는 slope 음전환",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 상단 채널 돌파 + 하락 추세
        if close > upper_channel and slope < 0:
            if confidence == Confidence.LOW:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"채널 상단 돌파 + 하락 추세: "
                    f"close={close:.2f} > upper={upper_channel:.2f}, slope={slope:.6f} < 0"
                ),
                invalidation=f"close < upper_channel 복귀 또는 slope 양전환",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=f"채널 내부 또는 조건 불일치: {context}",
            invalidation="채널 이탈 + slope 방향 일치 시 재평가",
            bull_case=context,
            bear_case=context,
        )
