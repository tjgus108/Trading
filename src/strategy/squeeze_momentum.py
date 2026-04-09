"""
Squeeze Momentum 전략:
- BB: middle=SMA20, upper=middle+2*std, lower=middle-2*std
- KC: middle=EMA20, upper=middle+1.5*ATR14, lower=middle-1.5*ATR14
- Squeeze ON  = BB upper < KC upper AND BB lower > KC lower
- Momentum    = close - mean(highest_high_20, lowest_low_20, SMA20)
- BUY:  squeeze 방금 해제(이전 ON, 현재 OFF) AND momentum > 0
- SELL: squeeze 방금 해제 AND momentum < 0
- confidence: HIGH if |momentum| > std(close,20), MEDIUM 그 외
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 25
_BB_MULT = 2.0
_KC_MULT = 1.5
_ATR_PERIOD = 14


def _calc_atr(df: pd.DataFrame, period: int = _ATR_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def _squeeze_signals(df: pd.DataFrame):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # BB
    sma20 = close.rolling(_PERIOD).mean()
    std20 = close.rolling(_PERIOD).std(ddof=0)
    bb_upper = sma20 + _BB_MULT * std20
    bb_lower = sma20 - _BB_MULT * std20

    # KC
    ema20 = close.ewm(span=_PERIOD, adjust=False).mean()
    atr14 = _calc_atr(df)
    kc_upper = ema20 + _KC_MULT * atr14
    kc_lower = ema20 - _KC_MULT * atr14

    # Squeeze
    squeeze = (bb_upper < kc_upper) & (bb_lower > kc_lower)

    # Momentum
    highest_high = high.rolling(_PERIOD).max()
    lowest_low = low.rolling(_PERIOD).min()
    momentum = close - (highest_high + lowest_low + sma20) / 3.0

    return squeeze, momentum, std20


class SqueezeMomentumStrategy(BaseStrategy):
    name = "squeeze_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        squeeze, momentum, std20 = _squeeze_signals(df)
        idx = len(df) - 2
        entry = float(df["close"].iloc[idx])

        sq_now = bool(squeeze.iloc[idx])
        sq_prev = bool(squeeze.iloc[idx - 1])
        mom_now = float(momentum.iloc[idx])
        std_now = float(std20.iloc[idx])

        # Squeeze 방금 해제 = 이전 ON, 현재 OFF
        just_released = sq_prev and not sq_now

        if just_released and mom_now > 0:
            conf = Confidence.HIGH if abs(mom_now) > std_now else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Squeeze 해제 + 양의 모멘텀: momentum={mom_now:.4f}",
                invalidation="모멘텀 음전환 또는 squeeze 재진입",
                bull_case=f"momentum={mom_now:.4f} > 0, squeeze 에너지 방출",
                bear_case="모멘텀 약화 가능성",
            )

        if just_released and mom_now < 0:
            conf = Confidence.HIGH if abs(mom_now) > std_now else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Squeeze 해제 + 음의 모멘텀: momentum={mom_now:.4f}",
                invalidation="모멘텀 양전환 또는 squeeze 재진입",
                bull_case="모멘텀 약화 가능성",
                bear_case=f"momentum={mom_now:.4f} < 0, squeeze 에너지 방출",
            )

        sq_state = "ON" if sq_now else "OFF"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Squeeze={sq_state}, momentum={mom_now:.4f}, 신호 없음",
            invalidation="",
            bull_case="",
            bear_case="",
        )
