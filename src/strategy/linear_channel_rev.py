"""
LinearChannelReversionStrategy: Linear Regression Channel 이탈 후 복귀 (mean reversion).
ENHANCED v3:
- 변동성 필터: ATR14 기반 (더 완화된 임계값)
- 편차 임계값: 2.7 (원래 2.5 대비 강화)
- 채널 너비 체크: channel_std > 0.2 (거짓신호 필터)
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_PERIOD = 30
_BAND_MULT = 2.0
_HIGH_CONF_MULT = 2.7  # 2.5 → 2.7: 중간 강화
_MIN_CHANNEL_STD = 0.2  # 완화된 채널 너비 (가짜신호 방지는 하되 과도하지 않음)
_MIN_ATR_RATIO = 0.0005  # 매우 완화 (거의 모든 상황 허용)


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
    """Linear Regression Channel 복귀 전략 (Enhanced v3)."""

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

        # ✅ ATR14 변동성 필터 (매우 완화)
        atr_ratio = 0.0  # 기본값
        if "atr14" in df.columns:
            atr_val = float(df["atr14"].iloc[idx])
            atr_ratio = atr_val / curr_close if not np.isnan(atr_val) and curr_close > 0 else 0.0
        
        # 변동성 필터를 거의 무시 (매우 낮은 임계값)
        if atr_ratio < _MIN_ATR_RATIO and atr_ratio != 0.0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"극저 변동성: ATR14/close={atr_ratio:.6f}",
                invalidation="변동성 증가 후 재시도",
            )

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

        # ✅ 채널 너비 필터: 최소한의 볼라틱만 필요
        if channel_std < _MIN_CHANNEL_STD:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"채널 너비 미달: channel_std={channel_std:.4f} < {_MIN_CHANNEL_STD:.4f}",
                invalidation="채널 너비 증가 후 재시도",
            )

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
            f"deviation={deviation:.4f} atr_ratio={atr_ratio:.6f}"
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
