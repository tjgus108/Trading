"""
LinearChannelReversionStrategy: Linear Regression Channel 이탈 후 복귀 (mean reversion).

- 최근 30봉 선형 회귀: numpy polyfit degree=1
- predicted = np.polyval(np.polyfit(range(30), close_30, 1), range(30))
- residuals = close_30 - predicted
- channel_std = residuals.std()
- upper = predicted[-1] + 2 * channel_std
- lower = predicted[-1] - 2 * channel_std
- BUY:  prev_close < lower AND curr_close >= lower (채널 하단 이탈 후 복귀)
- SELL: prev_close > upper AND curr_close <= upper (채널 상단 이탈 후 복귀)
- confidence: deviation > 2.5 * channel_std → HIGH, else MEDIUM
- 최소 데이터: 35행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_PERIOD = 30
_BAND_MULT = 2.0
_HIGH_CONF_MULT = 2.5


def _calc_channel(close_30: np.ndarray):
    """
    Returns (upper, lower, channel_std, deviation) for the last bar.
    deviation = abs(close_30[-1] - predicted[-1])
    """
    x = np.arange(_PERIOD, dtype=float)
    coeffs = np.polyfit(x, close_30, 1)
    predicted = np.polyval(coeffs, x)
    residuals = close_30 - predicted
    channel_std = float(residuals.std())
    pred_last = float(predicted[-1])
    upper = pred_last + _BAND_MULT * channel_std
    lower = pred_last - _BAND_MULT * channel_std
    deviation = abs(float(close_30[-1]) - pred_last)
    return upper, lower, channel_std, deviation


class LinearChannelReversionStrategy(BaseStrategy):
    """Linear Regression Channel 복귀 전략."""

    name = "linear_channel_rev"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            close_val = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"데이터 부족: {len(df)}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
            )

        # 신호 기준 인덱스: iloc[-2]
        idx = len(df) - 2
        prev_idx = idx - 1

        curr_close = float(df["close"].iloc[idx])
        prev_close = float(df["close"].iloc[prev_idx])

        # 최근 30봉 (현재봉 기준)
        window_start = max(0, idx - _PERIOD + 1)
        close_30 = df["close"].iloc[window_start: idx + 1].values.astype(float)

        if len(close_30) < _PERIOD:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"채널 계산 데이터 부족: {len(close_30)}봉 < {_PERIOD}봉",
                invalidation="데이터 충분 후 재시도",
            )

        upper, lower, channel_std, deviation = _calc_channel(close_30)

        # prev_close 기준 채널 계산 (이전 봉의 채널)
        prev_window_start = max(0, prev_idx - _PERIOD + 1)
        prev_close_30 = df["close"].iloc[prev_window_start: prev_idx + 1].values.astype(float)
        if len(prev_close_30) >= _PERIOD:
            prev_upper, prev_lower, _, _ = _calc_channel(prev_close_30)
        else:
            prev_upper, prev_lower = upper, lower

        confidence = Confidence.HIGH if deviation > _HIGH_CONF_MULT * channel_std else Confidence.MEDIUM

        context = (
            f"curr_close={curr_close:.4f} prev_close={prev_close:.4f} "
            f"upper={upper:.4f} lower={lower:.4f} channel_std={channel_std:.4f} "
            f"deviation={deviation:.4f}"
        )

        # BUY: prev_close < lower AND curr_close >= lower
        if prev_close < prev_lower and curr_close >= lower:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"채널 하단 이탈 후 복귀: prev_close={prev_close:.4f} < lower={prev_lower:.4f}, "
                    f"curr_close={curr_close:.4f} >= lower={lower:.4f}"
                ),
                invalidation=f"close < lower({lower:.4f}) 재이탈 시 무효",
                bull_case=context,
                bear_case=context,
            )

        # SELL: prev_close > upper AND curr_close <= upper
        if prev_close > prev_upper and curr_close <= upper:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"채널 상단 이탈 후 복귀: prev_close={prev_close:.4f} > upper={prev_upper:.4f}, "
                    f"curr_close={curr_close:.4f} <= upper={upper:.4f}"
                ),
                invalidation=f"close > upper({upper:.4f}) 재이탈 시 무효",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=f"채널 복귀 조건 미충족: {context}",
            invalidation="채널 이탈 후 복귀 시 재평가",
            bull_case=context,
            bear_case=context,
        )
