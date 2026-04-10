"""
TrendQualityFilterStrategy:
- BUY:  trend_consistency > 0.4 AND momentum > 0 AND pos_pct > 0.6
- SELL: trend_consistency > 0.4 AND momentum < 0 AND neg_pct > 0.6
- confidence: HIGH if trend_consistency > 0.6 else MEDIUM
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class TrendQualityFilterStrategy(BaseStrategy):
    name = "trend_quality_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        returns = close.pct_change().fillna(0)

        pos_pct = (returns > 0).rolling(20, min_periods=1).mean()
        neg_pct = (returns < 0).rolling(20, min_periods=1).mean()
        trend_consistency = (pos_pct - neg_pct).abs()

        momentum = close.pct_change(10)

        idx = len(df) - 2
        last = self._last(df)

        tc_val = trend_consistency.iloc[idx]
        mom_val = momentum.iloc[idx]
        pos_val = pos_pct.iloc[idx]
        neg_val = neg_pct.iloc[idx]

        if any(v != v for v in [tc_val, mom_val, pos_val, neg_val]):
            return self._hold(df, "NaN in indicators")

        close_price = float(last["close"])
        context = (
            f"trend_consistency={tc_val:.4f} momentum={mom_val:.4f} "
            f"pos_pct={pos_val:.4f} neg_pct={neg_val:.4f}"
        )

        if tc_val > 0.4 and mom_val > 0 and pos_val > 0.6:
            confidence = Confidence.HIGH if tc_val > 0.6 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=f"상승 추세 품질 우수: consistency={tc_val:.4f}>0.4, momentum={mom_val:.4f}>0, pos_pct={pos_val:.4f}>0.6",
                invalidation="trend_consistency < 0.4 or momentum turns negative",
                bull_case=context,
                bear_case=context,
            )

        if tc_val > 0.4 and mom_val < 0 and neg_val > 0.6:
            confidence = Confidence.HIGH if tc_val > 0.6 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=f"하락 추세 품질 우수: consistency={tc_val:.4f}>0.4, momentum={mom_val:.4f}<0, neg_pct={neg_val:.4f}>0.6",
                invalidation="trend_consistency < 0.4 or momentum turns positive",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close_price = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
