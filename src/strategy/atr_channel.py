"""
ATR Channel Breakout 전략.

지표:
  mid   = SMA(close, 20)
  ATR14 = atr14 컬럼 사용 (없으면 자체 계산)
  upper = mid + multiplier * ATR14  (multiplier=2.0)
  lower = mid - multiplier * ATR14

BUY:  close > upper (상방 채널 돌파)
SELL: close < lower (하방 채널 돌파)
confidence: HIGH if 돌파폭 > ATR14 * 0.5, MEDIUM 그 외
최소 데이터: 25행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_SMA_PERIOD = 20
_ATR_PERIOD = 14
_MULTIPLIER = 2.0
_MIN_ROWS = 25


def _compute_atr(df: pd.DataFrame, period: int = _ATR_PERIOD) -> pd.Series:
    """True Range 기반 ATR 계산 (atr14 컬럼 없을 때 폴백)."""
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.rolling(period).mean()


class ATRChannelStrategy(BaseStrategy):
    name = "atr_channel"

    def __init__(self, multiplier: float = _MULTIPLIER):
        self.multiplier = multiplier

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]) if len(df) > 0 else 0.0,
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="",
            )

        close = df["close"]
        mid = close.rolling(_SMA_PERIOD).mean()

        if "atr14" in df.columns:
            atr = df["atr14"]
        else:
            atr = _compute_atr(df)

        upper = mid + self.multiplier * atr
        lower = mid - self.multiplier * atr

        # _last(df) = df.iloc[-2] 패턴
        last = self._last(df)
        idx = -2

        last_close = float(close.iloc[idx])
        last_upper = float(upper.iloc[idx])
        last_lower = float(lower.iloc[idx])
        last_mid = float(mid.iloc[idx])
        last_atr = float(atr.iloc[idx])

        if np.isnan(last_upper) or np.isnan(last_lower) or np.isnan(last_atr):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="채널 계산 불가 (NaN).",
                invalidation="",
            )

        breakout_up = last_close > last_upper
        breakout_down = last_close < last_lower
        threshold = last_atr * 0.5

        if breakout_up:
            breakout_size = last_close - last_upper
            confidence = Confidence.HIGH if breakout_size > threshold else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"상방 채널 돌파. close={last_close:.4f} > upper={last_upper:.4f}, "
                    f"돌파폭={breakout_size:.4f}, ATR={last_atr:.4f}"
                ),
                invalidation=f"Close가 upper({last_upper:.4f}) 아래로 복귀 시 무효.",
                bull_case=f"ATR 채널 상방 돌파: 강한 상승 모멘텀.",
                bear_case="False breakout 가능성.",
            )

        if breakout_down:
            breakout_size = last_lower - last_close
            confidence = Confidence.HIGH if breakout_size > threshold else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"하방 채널 돌파. close={last_close:.4f} < lower={last_lower:.4f}, "
                    f"돌파폭={breakout_size:.4f}, ATR={last_atr:.4f}"
                ),
                invalidation=f"Close가 lower({last_lower:.4f}) 위로 복귀 시 무효.",
                bull_case="단기 반등 가능성.",
                bear_case=f"ATR 채널 하방 돌파: 강한 하락 모멘텀.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=last_close,
            reasoning=(
                f"채널 내부. close={last_close:.4f}, "
                f"upper={last_upper:.4f}, lower={last_lower:.4f}, mid={last_mid:.4f}"
            ),
            invalidation="",
        )
