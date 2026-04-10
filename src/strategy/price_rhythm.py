"""
PriceRhythmStrategy:
- 가격 리듬 (고점-저점 교대 패턴 + 타이밍)
- BUY:  rhythm_sum > 2 AND rhythm_change > 0 AND volume > vol_ma
- SELL: rhythm_sum < -2 AND rhythm_change < 0 AND volume > vol_ma
- confidence: HIGH if abs(rhythm_sum) >= 4 else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class PriceRhythmStrategy(BaseStrategy):
    name = "price_rhythm"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        volume = df["volume"]

        up_bar = close > close.shift(1)
        down_bar = close < close.shift(1)
        rhythm = up_bar.astype(int) - down_bar.astype(int)
        rhythm_sum = rhythm.rolling(5, min_periods=1).sum()
        rhythm_change = rhythm_sum.diff()
        vol_ma = volume.rolling(10, min_periods=1).mean()

        idx = len(df) - 2
        rs_now = rhythm_sum.iloc[idx]
        rc_now = rhythm_change.iloc[idx]
        vol_now = volume.iloc[idx]
        vm_now = vol_ma.iloc[idx]

        if any(v != v for v in [rs_now, rc_now, vol_now, vm_now]):  # NaN check
            return self._hold(df, "NaN in indicators")

        last = self._last(df)
        entry = float(last["close"])
        context = f"rhythm_sum={rs_now:.0f} rhythm_change={rc_now:.0f} vol_ratio={vol_now/vm_now:.2f}"

        if rs_now > 2 and rc_now > 0 and vol_now > vm_now:
            confidence = Confidence.HIGH if abs(rs_now) >= 4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"상승 리듬 강화: {context}",
                invalidation=f"rhythm_sum <= 2 or volume <= vol_ma",
                bull_case=context,
                bear_case=context,
            )

        if rs_now < -2 and rc_now < 0 and vol_now > vm_now:
            confidence = Confidence.HIGH if abs(rs_now) >= 4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"하락 리듬 강화: {context}",
                invalidation=f"rhythm_sum >= -2 or volume <= vol_ma",
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
