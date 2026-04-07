"""
EMA Cross 전략: EMA20이 EMA50을 상향 돌파 시 BUY, 하향 돌파 시 SELL.
실전 사례에서 수익성이 검증된 모멘텀 전략.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EmaCrossStrategy(BaseStrategy):
    name = "ema_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        prev = df.iloc[-3]
        last = self._last(df)

        ema20_crossed_up = prev["ema20"] <= prev["ema50"] and last["ema20"] > last["ema50"]
        ema20_crossed_down = prev["ema20"] >= prev["ema50"] and last["ema20"] < last["ema50"]

        rsi = last["rsi14"]
        entry = last["close"]

        bull_case = f"EMA20 ({last['ema20']:.2f}) > EMA50 ({last['ema50']:.2f}), RSI={rsi:.1f}"
        bear_case = f"EMA20 ({last['ema20']:.2f}) < EMA50 ({last['ema50']:.2f}), RSI={rsi:.1f}"

        if ema20_crossed_up and rsi < 70:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if rsi > 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"EMA20 crossed above EMA50. RSI={rsi:.1f} not overbought.",
                invalidation=f"Close below EMA50 ({last['ema50']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if ema20_crossed_down and rsi > 30:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if rsi < 50 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"EMA20 crossed below EMA50. RSI={rsi:.1f} not oversold.",
                invalidation=f"Close above EMA50 ({last['ema50']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning="No EMA crossover detected.",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
