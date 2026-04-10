"""
KeltnerChannelV2Strategy: EMA 기반 Keltner Channel 평균 회귀 전략.
- BUY:  close < lower (채널 하단 이탈) AND close > prev_close (반등 확인)
- SELL: close > upper (채널 상단 이탈) AND close < prev_close (반락 확인)
- confidence: HIGH if abs(close - ema20) > atr14 * 2.5 else MEDIUM
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class KeltnerChannelV2Strategy(BaseStrategy):
    name = "keltner_channel_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        close = df["close"].iloc[: idx + 1]
        high = df["high"].iloc[: idx + 1]
        low = df["low"].iloc[: idx + 1]

        ema20 = close.ewm(span=20, adjust=False).mean()
        atr14 = (high - low).rolling(14, min_periods=1).mean()

        upper = ema20 + atr14 * 2.0
        lower = ema20 - atr14 * 2.0

        last = self._last(df)
        c = float(last["close"])
        prev_c = float(df["close"].iloc[idx - 1]) if idx >= 1 else c

        ema20_val = float(ema20.iloc[-1])
        atr14_val = float(atr14.iloc[-1])
        upper_val = float(upper.iloc[-1])
        lower_val = float(lower.iloc[-1])

        if pd.isna(ema20_val) or pd.isna(atr14_val):
            return self._hold(df, "NaN indicator")

        dist = abs(c - ema20_val)
        confidence = (
            Confidence.HIGH if dist > atr14_val * 2.5 else Confidence.MEDIUM
        )

        if c < lower_val and c > prev_c:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"close({c:.4f}) < lower({lower_val:.4f}), bouncing",
                invalidation=f"close < {lower_val * 0.99:.4f}",
                bull_case="Mean reversion from lower band",
                bear_case="Breakdown below channel",
            )

        if c > upper_val and c < prev_c:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"close({c:.4f}) > upper({upper_val:.4f}), reversing",
                invalidation=f"close > {upper_val * 1.01:.4f}",
                bull_case="Momentum continuation above channel",
                bear_case="Mean reversion from upper band",
            )

        return self._hold(df, "No signal")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
