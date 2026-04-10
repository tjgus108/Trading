"""
VolatilityBreakoutV2Strategy: ATR 배수 기반 돌파 전략.

계산:
  atr14 = rolling ATR(14)
  prev_close = close.shift(1)
  upper = prev_close + 0.5 * atr14
  lower = prev_close - 0.5 * atr14

BUY:  curr_close > upper.iloc[idx]  (ATR 기반 상단 돌파)
SELL: curr_close < lower.iloc[idx]  (ATR 기반 하단 붕괴)
HOLD: lower <= curr_close <= upper

confidence: HIGH if (curr_close - upper.iloc[idx]) / atr14.iloc[idx] > 0.3 else MEDIUM
최소 20행 필요
"""

import pandas as pd
import numpy as np

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ATR_MULT = 0.5
_HIGH_CONF_THRESHOLD = 0.3


def _calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


class VolatilityBreakoutV2Strategy(BaseStrategy):
    name = "volatility_breakout_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for VolatilityBreakoutV2",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        atr14 = _calc_atr(df, 14)
        prev_close = df["close"].shift(1)
        upper = prev_close + _ATR_MULT * atr14
        lower = prev_close - _ATR_MULT * atr14

        curr_close = float(df["close"].iloc[idx])
        atr_val = float(atr14.iloc[idx])
        ul = float(upper.iloc[idx])
        ll = float(lower.iloc[idx])

        if pd.isna(atr_val) or atr_val <= 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close,
                reasoning="ATR NaN or <= 0, no signal",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        if curr_close > ul:
            ratio = (curr_close - ul) / atr_val
            conf = Confidence.HIGH if ratio > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"ATR 상단 돌파: close {curr_close:.2f} > upper {ul:.2f}, "
                    f"atr14 {atr_val:.2f}, ratio {ratio:.3f}"
                ),
                invalidation=f"close falls below upper {ul:.2f}",
                bull_case=f"ATR 대비 {ratio:.1%} 상단 돌파",
                bear_case="False breakout 가능",
            )

        if curr_close < ll:
            ratio = (ll - curr_close) / atr_val
            conf = Confidence.HIGH if ratio > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"ATR 하단 붕괴: close {curr_close:.2f} < lower {ll:.2f}, "
                    f"atr14 {atr_val:.2f}, ratio {ratio:.3f}"
                ),
                invalidation=f"close rises above lower {ll:.2f}",
                bull_case="단순 조정일 수 있음",
                bear_case=f"ATR 대비 {ratio:.1%} 하단 돌파",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"ATR 범위 내: close {curr_close:.2f}, "
                f"upper {ul:.2f}, lower {ll:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
