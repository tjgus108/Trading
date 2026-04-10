"""
TrendIntensityIndex Strategy (새 버전):
- TII = (above - below) / period * 100  (-100 ~ +100)
- tii_ma = TII.rolling(9).mean()
- BUY:  tii crosses above tii_ma AND tii < 0 (이전 tii < tii_ma, 현재 tii >= tii_ma, 음수 구간)
- SELL: tii crosses below tii_ma AND tii > 0
- confidence: HIGH if abs(tii) > 40 else MEDIUM
- 최소 45행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 45
_PERIOD = 30
_MA_PERIOD = 9


class TrendIntensityIndexV2Strategy(BaseStrategy):
    name = "trend_intensity_index"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"Insufficient data for TrendIntensityIndex: {len(df)} rows (min {_MIN_ROWS})")

        close = df["close"]
        sma30 = close.rolling(_PERIOD).mean()

        above = (close > sma30).rolling(_PERIOD).sum()
        below = (close < sma30).rolling(_PERIOD).sum()

        tii = (above - below) / _PERIOD * 100
        tii_ma = tii.rolling(_MA_PERIOD).mean()

        idx = len(df) - 2

        tii_curr = tii.iloc[idx]
        tii_prev = tii.iloc[idx - 1]
        tii_ma_curr = tii_ma.iloc[idx]
        tii_ma_prev = tii_ma.iloc[idx - 1]

        entry_price = float(df.iloc[idx]["close"])

        # NaN guard
        for val in (tii_curr, tii_prev, tii_ma_curr, tii_ma_prev):
            if val != val:
                return self._hold(df, "NaN in TII calculation")

        tii_val = float(tii_curr)
        tii_ma_val = float(tii_ma_curr)

        context = f"tii={tii_val:.2f} tii_ma={tii_ma_val:.2f}"

        conf = Confidence.HIGH if abs(tii_val) > 40 else Confidence.MEDIUM

        # BUY: tii crosses above tii_ma AND tii < 0
        if float(tii_prev) < float(tii_ma_prev) and tii_val >= tii_ma_val and tii_val < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"TII crosses above tii_ma in bearish zone: {context}",
                invalidation=f"tii drops below tii_ma again",
                bull_case=f"TII recovering from negative zone, potential reversal",
                bear_case=f"tii still negative, trend may continue down",
            )

        # SELL: tii crosses below tii_ma AND tii > 0
        if float(tii_prev) > float(tii_ma_prev) and tii_val <= tii_ma_val and tii_val > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"TII crosses below tii_ma in bullish zone: {context}",
                invalidation=f"tii rises above tii_ma again",
                bull_case=f"tii still positive, trend may continue up",
                bear_case=f"TII weakening from positive zone, potential reversal",
            )

        return self._hold(df, f"No TII signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
