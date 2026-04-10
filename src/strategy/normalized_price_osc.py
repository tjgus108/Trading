"""
NormalizedPriceOscStrategy: rolling min-max 정규화로 사이클 신호 생성.
- npo = (close - rolling_min) / (rolling_max - rolling_min + 1e-10) * 100  # 0~100
- BUY: npo crosses above 20 AND npo > npo_ma
- SELL: npo crosses below 80 AND npo < npo_ma
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class NormalizedPriceOscStrategy(BaseStrategy):
    name = "normalized_price_osc"

    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, "Insufficient data for NormalizedPriceOsc (need 25 rows)")

        close = df["close"]
        rolling_max = close.rolling(20).max()
        rolling_min = close.rolling(20).min()
        npo = (close - rolling_min) / (rolling_max - rolling_min + 1e-10) * 100
        npo_ma = npo.rolling(5).mean()

        idx = len(df) - 2
        curr_npo = npo.iloc[idx]
        prev_npo = npo.iloc[idx - 1]
        curr_npo_ma = npo_ma.iloc[idx]

        if pd.isna(curr_npo) or pd.isna(prev_npo) or pd.isna(curr_npo_ma):
            return self._hold(df, "Insufficient data for NormalizedPriceOsc (NaN detected)")

        last = self._last(df)
        entry = float(last["close"])

        crosses_above_20 = prev_npo < 20 and curr_npo >= 20
        crosses_below_80 = prev_npo > 80 and curr_npo <= 80

        if crosses_above_20 and curr_npo > curr_npo_ma:
            confidence = Confidence.HIGH if curr_npo < 10 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"NPO crossed above 20: prev={prev_npo:.1f} -> curr={curr_npo:.1f}, "
                    f"npo_ma={curr_npo_ma:.1f}"
                ),
                invalidation=f"NPO drops back below 15",
                bull_case=f"NPO={curr_npo:.1f} > npo_ma={curr_npo_ma:.1f}, oversold recovery",
                bear_case=f"NPO still low, trend may continue down",
            )

        if crosses_below_80 and curr_npo < curr_npo_ma:
            confidence = Confidence.HIGH if curr_npo > 90 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"NPO crossed below 80: prev={prev_npo:.1f} -> curr={curr_npo:.1f}, "
                    f"npo_ma={curr_npo_ma:.1f}"
                ),
                invalidation=f"NPO recovers back above 85",
                bull_case=f"NPO still elevated, may bounce",
                bear_case=f"NPO={curr_npo:.1f} < npo_ma={curr_npo_ma:.1f}, overbought reversal",
            )

        return self._hold(
            df,
            f"No signal: NPO={curr_npo:.1f}, prev={prev_npo:.1f}, npo_ma={curr_npo_ma:.1f}",
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
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
