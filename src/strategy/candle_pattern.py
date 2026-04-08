"""
Candle Pattern 전략:
- Hammer (망치형): lower_wick > body*2, 양봉, RSI < 45 → BUY
- Shooting Star (유성형): upper_wick > body*2, 음봉, RSI > 55 → SELL
- Bullish Engulfing: 현재 양봉 body가 전봉 음봉 body를 완전히 감싸면 → BUY
- Bearish Engulfing: 현재 음봉 body가 전봉 양봉 body를 완전히 감싸면 → SELL
- confidence: HIGH(2개 이상 패턴 동시), MEDIUM(1개 패턴)
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class CandlePatternStrategy(BaseStrategy):
    name = "candle_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        prev = df.iloc[-3]  # 직전 완성 캔들

        close = float(last["close"])
        open_ = float(last["open"])
        high = float(last["high"])
        low = float(last["low"])
        rsi = float(last.get("rsi", 50))

        prev_close = float(prev["close"])
        prev_open = float(prev["open"])

        patterns_buy = []
        patterns_sell = []

        # 1. Hammer
        body = abs(close - open_)
        if body > 0 and close > open_:
            lower_wick = open_ - low
            if lower_wick > body * 2 and rsi < 45:
                patterns_buy.append("hammer")

        # 2. Shooting Star
        body = abs(close - open_)
        if body > 0 and close < open_:
            upper_wick = high - close
            if upper_wick > body * 2 and rsi > 55:
                patterns_sell.append("shooting_star")

        # 3. Engulfing
        prev_body_top = max(prev_close, prev_open)
        prev_body_bot = min(prev_close, prev_open)
        curr_body_top = max(close, open_)
        curr_body_bot = min(close, open_)

        prev_is_bearish = prev_close < prev_open
        prev_is_bullish = prev_close > prev_open
        curr_is_bullish = close > open_
        curr_is_bearish = close < open_

        if curr_is_bullish and prev_is_bearish:
            if curr_body_top > prev_body_top and curr_body_bot < prev_body_bot:
                patterns_buy.append("bullish_engulfing")

        if curr_is_bearish and prev_is_bullish:
            if curr_body_top > prev_body_top and curr_body_bot < prev_body_bot:
                patterns_sell.append("bearish_engulfing")

        # 신호 결정
        all_buy = len(patterns_buy)
        all_sell = len(patterns_sell)

        if all_buy > 0 and all_buy >= all_sell:
            confidence = Confidence.HIGH if all_buy >= 2 else Confidence.MEDIUM
            reason = f"Bullish patterns: {patterns_buy}"
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=reason,
                invalidation=f"Close below low ({low:.2f})",
                bull_case=reason,
                bear_case="",
            )

        if all_sell > 0:
            confidence = Confidence.HIGH if all_sell >= 2 else Confidence.MEDIUM
            reason = f"Bearish patterns: {patterns_sell}"
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=reason,
                invalidation=f"Close above high ({high:.2f})",
                bull_case="",
                bear_case=reason,
            )

        return self._hold(df, f"No pattern: rsi={rsi:.1f} close={close:.2f}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df) if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
