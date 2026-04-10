"""
KijunBounceStrategy:
- Ichimoku Kijun-sen(26기간)을 동적 지지/저항으로 사용
- BUY: close가 kijun ±0.5% 내 터치 AND 양봉(close > open) AND cloud bullish(tenkan > kijun)
- SELL: close가 kijun ±0.5% 내 터치 AND 음봉(close < open) AND cloud bearish(tenkan < kijun)
- confidence: kijun 방향(rising=bullish, falling=bearish) 일치 → HIGH, 그 외 MEDIUM
- 최소 데이터: 30행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_TENKAN_PERIOD = 9
_KIJUN_PERIOD = 26
_TOUCH_PCT = 0.005  # ±0.5%


class KijunBounceStrategy(BaseStrategy):
    name = "kijun_bounce"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2  # _last() 기준

        # Kijun-sen (26기간)
        kijun_high = df["high"].iloc[idx - _KIJUN_PERIOD + 1: idx + 1].max()
        kijun_low = df["low"].iloc[idx - _KIJUN_PERIOD + 1: idx + 1].min()
        kijun = (float(kijun_high) + float(kijun_low)) / 2

        # Tenkan-sen (9기간)
        tenkan_high = df["high"].iloc[idx - _TENKAN_PERIOD + 1: idx + 1].max()
        tenkan_low = df["low"].iloc[idx - _TENKAN_PERIOD + 1: idx + 1].min()
        tenkan = (float(tenkan_high) + float(tenkan_low)) / 2

        # kijun 방향: 현재 kijun vs 1봉 전 kijun
        if idx >= _KIJUN_PERIOD:
            prev_kijun_high = df["high"].iloc[idx - _KIJUN_PERIOD: idx].max()
            prev_kijun_low = df["low"].iloc[idx - _KIJUN_PERIOD: idx].min()
            prev_kijun = (float(prev_kijun_high) + float(prev_kijun_low)) / 2
        else:
            prev_kijun = kijun

        kijun_rising = kijun > prev_kijun
        kijun_falling = kijun < prev_kijun

        last = self._last(df)
        close = float(last["close"])
        open_ = float(last["open"])

        # kijun ±0.5% 터치 여부
        if kijun == 0:
            return self._hold(df, "kijun is zero")
        dist_pct = abs(close - kijun) / kijun
        touching_kijun = dist_pct <= _TOUCH_PCT

        context = (
            f"close={close:.4f} kijun={kijun:.4f} tenkan={tenkan:.4f} "
            f"dist={dist_pct:.4f} kijun_rising={kijun_rising}"
        )

        # BUY: 양봉 + kijun 터치 + cloud bullish
        if touching_kijun and close > open_ and tenkan > kijun:
            confidence = Confidence.HIGH if kijun_rising else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Kijun 반등 BUY: close({close:.4f}) kijun({kijun:.4f}) 터치 "
                    f"dist={dist_pct:.4f} 양봉 cloud_bullish tenkan({tenkan:.4f})>kijun"
                ),
                invalidation=f"Close below Kijun ({kijun:.4f}) or tenkan < kijun",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 음봉 + kijun 터치 + cloud bearish
        if touching_kijun and close < open_ and tenkan < kijun:
            confidence = Confidence.HIGH if kijun_falling else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Kijun 저항 SELL: close({close:.4f}) kijun({kijun:.4f}) 터치 "
                    f"dist={dist_pct:.4f} 음봉 cloud_bearish tenkan({tenkan:.4f})<kijun"
                ),
                invalidation=f"Close above Kijun ({kijun:.4f}) or tenkan > kijun",
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
