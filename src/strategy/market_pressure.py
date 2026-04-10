"""
MarketPressureStrategy:
- BUY:  pressure_diff > 0.2 AND pressure_trend > pressure_ma AND volume > vol_ma
- SELL: pressure_diff < -0.2 AND pressure_trend < pressure_ma AND volume > vol_ma
- confidence: HIGH if |pressure_diff| > 0.4 else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class MarketPressureStrategy(BaseStrategy):
    name = "market_pressure"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        buying_pressure = close - low
        selling_pressure = high - close
        total_range = high - low + 1e-10

        buy_ratio = buying_pressure / total_range
        sell_ratio = selling_pressure / total_range
        pressure_diff = buy_ratio - sell_ratio

        pressure_ma = pressure_diff.rolling(10, min_periods=1).mean()
        pressure_trend = pressure_diff.rolling(3, min_periods=1).mean()
        vol_ma = volume.rolling(10, min_periods=1).mean()

        idx = len(df) - 2
        last = self._last(df)

        pd_val = pressure_diff.iloc[idx]
        pt_val = pressure_trend.iloc[idx]
        pm_val = pressure_ma.iloc[idx]
        vol_val = volume.iloc[idx]
        vm_val = vol_ma.iloc[idx]

        if any(v != v for v in [pd_val, pt_val, pm_val, vol_val, vm_val]):
            return self._hold(df, "NaN in indicators")

        close_price = float(last["close"])
        context = (
            f"pressure_diff={pd_val:.4f} pressure_trend={pt_val:.4f} "
            f"pressure_ma={pm_val:.4f} volume={vol_val:.0f} vol_ma={vm_val:.0f}"
        )

        vol_confirm = vol_val > vm_val

        if pd_val > 0.2 and pt_val > pm_val and vol_confirm:
            confidence = Confidence.HIGH if abs(pd_val) > 0.4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=f"매수 압력 우세: pressure_diff={pd_val:.4f}>0.2, trend>ma, vol>vol_ma",
                invalidation="pressure_diff < 0.2 or volume drops below average",
                bull_case=context,
                bear_case=context,
            )

        if pd_val < -0.2 and pt_val < pm_val and vol_confirm:
            confidence = Confidence.HIGH if abs(pd_val) > 0.4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=f"매도 압력 우세: pressure_diff={pd_val:.4f}<-0.2, trend<ma, vol>vol_ma",
                invalidation="pressure_diff > -0.2 or volume drops below average",
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
