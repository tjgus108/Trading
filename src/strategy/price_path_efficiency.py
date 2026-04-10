"""
PricePathEfficiencyStrategy:
- 가격 경로 효율성 (Fractal Efficiency Ratio의 간소화)
- BUY:  efficiency > 0.5 AND efficiency > efficiency_ma AND trend_up
- SELL: efficiency > 0.5 AND efficiency > efficiency_ma AND NOT trend_up
- confidence: HIGH if efficiency > 0.75 else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_LOOKBACK = 8


class PricePathEfficiencyStrategy(BaseStrategy):
    name = "price_path_efficiency"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        idx = len(df) - 2

        net_change = (close - close.shift(_LOOKBACK)).abs()
        total_path = close.diff().abs().rolling(_LOOKBACK, min_periods=1).sum()
        efficiency = net_change / (total_path + 1e-10)
        efficiency_ma = efficiency.rolling(5, min_periods=1).mean()
        trend_up = close > close.shift(_LOOKBACK)

        eff = float(efficiency.iloc[idx])
        eff_ma = float(efficiency_ma.iloc[idx])
        up = bool(trend_up.iloc[idx])
        price = float(close.iloc[idx])

        if pd.isna(eff) or pd.isna(eff_ma) or pd.isna(price):
            return self._hold(df, "NaN values detected")

        context = f"close={price:.2f} efficiency={eff:.4f} eff_ma={eff_ma:.4f} trend_up={up}"

        if eff > 0.5 and eff > eff_ma and up:
            confidence = Confidence.HIGH if eff > 0.75 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"High efficiency uptrend: eff={eff:.4f}>0.5, trend_up=True",
                invalidation=f"Efficiency drops below 0.5 or below eff_ma ({eff_ma:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if eff > 0.5 and eff > eff_ma and not up:
            confidence = Confidence.HIGH if eff > 0.75 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"High efficiency downtrend: eff={eff:.4f}>0.5, trend_up=False",
                invalidation=f"Efficiency drops below 0.5 or trend reverses",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

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
