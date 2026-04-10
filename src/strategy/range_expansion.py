"""
RangeExpansion 전략:
- bar_range = high - low
- avg_range = bar_range.rolling(14).mean()
- range_ratio = bar_range / avg_range
- close_pos = (close - low) / (high - low)  # 0~1, 1에 가까울수록 강세
- BUY: range_ratio > 1.5 AND close_pos > 0.7
- SELL: range_ratio > 1.5 AND close_pos < 0.3
- HOLD: range_ratio <= 1.5
- confidence: HIGH if range_ratio > 2.0 else MEDIUM
- 최소 데이터: 20행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20
RATIO_MED = 1.5
RATIO_HIGH = 2.0
CLOSE_POS_BUY = 0.7
CLOSE_POS_SELL = 0.3


class RangeExpansionStrategy(BaseStrategy):
    name = "range_expansion"

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            rows = len(df) if df is not None else 0
            return self._hold(df if df is not None else pd.DataFrame(), f"Insufficient data: {rows} < {MIN_ROWS}")

        high = df["high"]
        low = df["low"]
        close = df["close"]

        bar_range = high - low
        avg_range = bar_range.rolling(14).mean()

        idx = len(df) - 2

        bar_val = float(bar_range.iloc[idx])
        avg_val = float(avg_range.iloc[idx])

        if np.isnan(avg_val) or avg_val == 0:
            return self._hold(df, "avg_range 계산 불가 (NaN 또는 0)")

        range_ratio = bar_val / avg_val

        high_val = float(high.iloc[idx])
        low_val = float(low.iloc[idx])
        close_val = float(close.iloc[idx])

        if high_val == low_val:
            close_pos = 0.5
        else:
            close_pos = (close_val - low_val) / (high_val - low_val)

        if np.isnan(close_pos):
            close_pos = 0.5

        confidence = Confidence.HIGH if range_ratio > RATIO_HIGH else Confidence.MEDIUM

        reasoning_base = (
            f"range_ratio={range_ratio:.2f}, close_pos={close_pos:.2f}, "
            f"bar_range={bar_val:.4f}, avg_range={avg_val:.4f}"
        )

        if range_ratio > RATIO_MED and close_pos > CLOSE_POS_BUY:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"범위 확장 + 위쪽 마감. {reasoning_base}",
                invalidation=f"close_pos < {CLOSE_POS_BUY} 또는 range_ratio < {RATIO_MED}",
                bull_case=f"range_ratio={range_ratio:.2f}x 확장, close_pos={close_pos:.2f} 강세",
                bear_case="범위 확장 없거나 아래쪽 마감",
            )

        if range_ratio > RATIO_MED and close_pos < CLOSE_POS_SELL:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"범위 확장 + 아래쪽 마감. {reasoning_base}",
                invalidation=f"close_pos > {CLOSE_POS_SELL} 또는 range_ratio < {RATIO_MED}",
                bull_case="범위 확장 없거나 위쪽 마감",
                bear_case=f"range_ratio={range_ratio:.2f}x 확장, close_pos={close_pos:.2f} 약세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"범위 확장 미충족. {reasoning_base}",
            invalidation="",
            bull_case="range_ratio > 1.5 + close_pos > 0.7 필요",
            bear_case="range_ratio > 1.5 + close_pos < 0.3 필요",
        )
