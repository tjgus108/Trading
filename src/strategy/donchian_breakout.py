"""
Donchian Channel Breakout 전략: 20봉 최고가 돌파 시 BUY, 최저가 하향 돌파 시 SELL.
43.8% APR 사례에서 사용된 전략. 단순하지만 트렌드 추종에 강함.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class DonchianBreakoutStrategy(BaseStrategy):
    name = "donchian_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        prev = df.iloc[-3]
        last = self._last(df)

        broke_high = prev["close"] <= prev["donchian_high"] and last["close"] > last["donchian_high"]
        broke_low = prev["close"] >= prev["donchian_low"] and last["close"] < last["donchian_low"]

        entry = last["close"]
        rsi = last["rsi14"]
        atr = last["atr14"]

        bull_case = (
            f"Price ({entry:.2f}) broke above 20-bar high ({last['donchian_high']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}"
        )
        bear_case = (
            f"Price ({entry:.2f}) broke below 20-bar low ({last['donchian_low']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}"
        )

        if broke_high and rsi < 80:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if rsi < 70 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Breakout above Donchian high {last['donchian_high']:.2f}. RSI={rsi:.1f}.",
                invalidation=f"Close back below Donchian high ({last['donchian_high']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if broke_low and rsi > 20:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if rsi > 30 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Breakdown below Donchian low {last['donchian_low']:.2f}. RSI={rsi:.1f}.",
                invalidation=f"Close back above Donchian low ({last['donchian_low']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning="No Donchian channel breakout.",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
