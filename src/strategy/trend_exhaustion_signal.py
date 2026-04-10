"""
TrendExhaustionSignalStrategy: 추세 소진 신호.
장기 추세 후 반전 가능성을 과매수/과매도 비율과 ATR 스트레치로 감지한다.
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendExhaustionSignalStrategy(BaseStrategy):
    name = "trend_exhaustion_signal"

    _MIN_ROWS = 25

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < self._MIN_ROWS:
            price = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=price,
                reasoning="Insufficient data",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]

        lookback = 20
        trend_bars = (close > close.shift(1)).rolling(lookback, min_periods=1).sum()
        overshoot_up = trend_bars >= 16
        overshoot_down = trend_bars <= 4

        atr = (high - low).rolling(14, min_periods=1).mean()
        recent_move = abs(close - close.shift(5))
        stretch = recent_move / (atr + 1e-10)

        idx = len(df) - 2
        last = df.iloc[idx]
        entry = float(last["close"])

        tb = trend_bars.iloc[idx]
        ov_up = overshoot_up.iloc[idx]
        ov_down = overshoot_down.iloc[idx]
        st = stretch.iloc[idx]
        c = close.iloc[idx]
        c_prev = close.iloc[idx - 1] if idx >= 1 else float("nan")

        # NaN 체크
        if any(math.isnan(v) for v in [tb, st, c]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in indicators",
                invalidation="",
            )

        info = f"trend_bars={tb:.0f} stretch={st:.3f} close={c:.4f}"

        # BUY: 과도한 하락 후 반전 시작
        if ov_down and st > 1.5 and not math.isnan(c_prev) and c > c_prev:
            confidence = Confidence.HIGH if tb <= 2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Oversold exhaustion + reversal started. {info}",
                invalidation="close falls below recent low or trend_bars stays <= 4",
                bull_case="Downtrend exhausted, reversal candle confirms",
                bear_case="Continued downtrend despite oversold reading",
            )

        # SELL: 과도한 상승 후 반전 시작
        if ov_up and st > 1.5 and not math.isnan(c_prev) and c < c_prev:
            confidence = Confidence.HIGH if tb >= 18 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Overbought exhaustion + reversal started. {info}",
                invalidation="close rises above recent high or trend_bars stays >= 16",
                bull_case="Continued uptrend despite overbought reading",
                bear_case="Uptrend exhausted, reversal candle confirms",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"No exhaustion signal. {info}",
            invalidation="",
        )
