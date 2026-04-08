"""
Ichimoku Cloud 전략:
- Tenkan-sen (전환선) = (9봉 최고 + 9봉 최저) / 2
- Kijun-sen (기준선) = (26봉 최고 + 26봉 최저) / 2
- BUY:  Tenkan > Kijun (골든크로스) AND close > Kijun
- SELL: Tenkan < Kijun (데드크로스) AND close < Kijun
- HOLD: 그 외
- confidence: HIGH(close가 Kijun에서 1% 이상 이격), MEDIUM 그 외
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_HIGH_CONF_DISTANCE = 0.01  # 1% 이격


class IchimokuStrategy(BaseStrategy):
    name = "ichimoku"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])

        # Tenkan-sen: 최근 9봉 (현재 완성 캔들 포함, -2 인덱스 기준)
        idx = len(df) - 2  # _last()와 동일한 기준
        tenkan_slice = df["high"].iloc[idx - _TENKAN_PERIOD + 1: idx + 1]
        tenkan_low_slice = df["low"].iloc[idx - _TENKAN_PERIOD + 1: idx + 1]
        tenkan = (float(tenkan_slice.max()) + float(tenkan_low_slice.min())) / 2

        # Kijun-sen: 최근 26봉
        kijun_slice = df["high"].iloc[idx - _KIJUN_PERIOD + 1: idx + 1]
        kijun_low_slice = df["low"].iloc[idx - _KIJUN_PERIOD + 1: idx + 1]
        kijun = (float(kijun_slice.max()) + float(kijun_low_slice.min())) / 2

        distance_pct = abs(close - kijun) / kijun if kijun != 0 else 0.0
        confidence = Confidence.HIGH if distance_pct >= _HIGH_CONF_DISTANCE else Confidence.MEDIUM

        context = (
            f"close={close:.2f} tenkan={tenkan:.2f} kijun={kijun:.2f} "
            f"dist={distance_pct:.4f}"
        )

        if tenkan > kijun and close > kijun:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Ichimoku 골든크로스: tenkan({tenkan:.2f})>kijun({kijun:.2f}), "
                    f"close({close:.2f})>kijun"
                ),
                invalidation=f"Close below Kijun ({kijun:.2f}) or Tenkan < Kijun",
                bull_case=context,
                bear_case=context,
            )

        if tenkan < kijun and close < kijun:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Ichimoku 데드크로스: tenkan({tenkan:.2f})<kijun({kijun:.2f}), "
                    f"close({close:.2f})<kijun"
                ),
                invalidation=f"Close above Kijun ({kijun:.2f}) or Tenkan > Kijun",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: tenkan={tenkan:.2f} kijun={kijun:.2f} close={close:.2f}", context, context)

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
