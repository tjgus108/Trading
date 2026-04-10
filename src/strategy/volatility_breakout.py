"""
VolatilityBreakoutStrategy: Bollinger Band 확장 시 추세 추종 전략.

- bb_mid = close.rolling(20, min_periods=1).mean()
- bb_std = close.rolling(20, min_periods=1).std()
- bb_upper = bb_mid + bb_std * 2
- bb_lower = bb_mid - bb_std * 2
- bb_width = (bb_upper - bb_lower) / (bb_mid + 1e-10)
- bb_width_ma = bb_width.rolling(10, min_periods=1).mean()
- expanding = bb_width > bb_width_ma
- BUY:  expanding AND close > bb_upper
- SELL: expanding AND close < bb_lower
- confidence: HIGH if bb_width > bb_width_ma * 1.3, MEDIUM otherwise
- 최소 20행
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class VolatilityBreakoutStrategy(BaseStrategy):
    name = "volatility_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        bb_mid = close.rolling(20, min_periods=1).mean()
        bb_std = close.rolling(20, min_periods=1).std()
        bb_upper = bb_mid + bb_std * 2
        bb_lower = bb_mid - bb_std * 2
        bb_width = (bb_upper - bb_lower) / (bb_mid + 1e-10)
        bb_width_ma = bb_width.rolling(10, min_periods=1).mean()

        idx = len(df) - 2

        v_close = float(close.iloc[idx])
        v_bb_upper = float(bb_upper.iloc[idx])
        v_bb_lower = float(bb_lower.iloc[idx])
        v_bb_width = float(bb_width.iloc[idx])
        v_bb_width_ma = float(bb_width_ma.iloc[idx])

        if any(math.isnan(x) for x in [v_close, v_bb_upper, v_bb_lower, v_bb_width, v_bb_width_ma]):
            return self._hold(df, "NaN in indicators")

        expanding = v_bb_width > v_bb_width_ma
        is_high_conf = v_bb_width > v_bb_width_ma * 1.3

        context = (
            f"close={v_close:.4f} bb_upper={v_bb_upper:.4f} bb_lower={v_bb_lower:.4f} "
            f"bb_width={v_bb_width:.4f} bb_width_ma={v_bb_width_ma:.4f} expanding={expanding}"
        )

        if expanding and v_close > v_bb_upper:
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"Volatility Breakout BUY: close({v_close:.4f})>bb_upper({v_bb_upper:.4f}), "
                    f"bb_width={v_bb_width:.4f}>bb_width_ma={v_bb_width_ma:.4f}"
                ),
                invalidation="close<bb_upper or not expanding",
                bull_case=context,
                bear_case=context,
            )

        if expanding and v_close < v_bb_lower:
            confidence = Confidence.HIGH if is_high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=v_close,
                reasoning=(
                    f"Volatility Breakout SELL: close({v_close:.4f})<bb_lower({v_bb_lower:.4f}), "
                    f"bb_width={v_bb_width:.4f}>bb_width_ma={v_bb_width_ma:.4f}"
                ),
                invalidation="close>bb_lower or not expanding",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df) if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
