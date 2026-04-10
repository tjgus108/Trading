"""
PriceImpactStrategy: Kyle's Lambda 간소화 기반 가격 충격 전략.
- BUY: impact > impact_ma * 1.5 AND dir_ma > 0
- SELL: impact > impact_ma * 1.5 AND dir_ma < 0
- HOLD: 그 외
- confidence: HIGH if impact > impact_ma * 2.0 else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_IMPACT_MULT = 1.5
_HIGH_CONF_MULT = 2.0


class PriceImpactStrategy(BaseStrategy):
    name = "price_impact"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for PriceImpact")

        close = df["close"]

        price_change = close.diff().abs()
        impact = price_change / (df["volume"] + 1e-10) * 1000
        impact_ma = impact.ewm(span=20, adjust=False).mean()

        direction = close.diff()
        dir_ma = direction.ewm(span=10, adjust=False).mean()

        idx = len(df) - 2
        last = df.iloc[idx]

        impact_val = impact.iloc[idx]
        impact_ma_val = impact_ma.iloc[idx]
        dir_ma_val = dir_ma.iloc[idx]
        close_val = float(last["close"])

        if pd.isna(impact_val) or pd.isna(impact_ma_val) or pd.isna(dir_ma_val):
            return self._hold(df, "NaN in indicators")

        info = (
            f"impact={impact_val:.6f} impact_ma={impact_ma_val:.6f} "
            f"dir_ma={dir_ma_val:.4f} close={close_val:.2f}"
        )

        high_impact = impact_val > impact_ma_val * _IMPACT_MULT

        if high_impact and dir_ma_val > 0:
            confidence = (
                Confidence.HIGH
                if impact_val > impact_ma_val * _HIGH_CONF_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"High price impact + upward direction: {info}",
                invalidation=f"dir_ma turns negative or impact drops below threshold",
                bull_case=info,
                bear_case=info,
            )

        if high_impact and dir_ma_val < 0:
            confidence = (
                Confidence.HIGH
                if impact_val > impact_ma_val * _HIGH_CONF_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"High price impact + downward direction: {info}",
                invalidation=f"dir_ma turns positive or impact drops below threshold",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
