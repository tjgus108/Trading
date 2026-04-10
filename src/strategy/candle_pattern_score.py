"""
CandlePatternScoreStrategy: 여러 캔들 패턴을 점수화하여 종합 신호 생성.

패턴:
  - Hammer (+2), Shooting Star (-2)
  - Bullish/Bearish Engulfing (+/-2)
  - Strong Bullish/Bearish candle (+/-1)
  - Doji (neutral)

신호:
  - BUY: score >= 3
  - SELL: score <= -3
  - HOLD: -2 <= score <= 2
- confidence: HIGH if abs(score) >= 4 else MEDIUM
- 최소 행: 5
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 5


class CandlePatternScoreStrategy(BaseStrategy):
    name = "candle_pattern_score"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for candle_pattern_score")

        idx = len(df) - 2  # 마지막 완성봉

        row = df.iloc[idx]
        prev = df.iloc[idx - 1]

        try:
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            po = float(prev["open"])
            ph = float(prev["high"])
            pl = float(prev["low"])
            pc = float(prev["close"])
        except (KeyError, TypeError, ValueError):
            return self._hold(df, "Insufficient data for candle_pattern_score")

        import math
        if any(math.isnan(v) for v in [o, h, l, c, po, ph, pl, pc]):
            return self._hold(df, "Insufficient data for candle_pattern_score")

        body = abs(c - o)
        total = max(h - l, 0.0001)
        body_ratio = body / total

        lower_wick = min(o, c) - l
        upper_wick = h - max(o, c)

        score = 0

        # 1. Hammer
        if lower_wick > body * 2 and upper_wick < body * 0.5 and pc < po:
            score += 2  # bullish

        # 2. Shooting Star
        if upper_wick > body * 2 and lower_wick < body * 0.5 and pc > po:
            score -= 2  # bearish

        # 3. Bullish engulfing
        if c > o and pc < po and c > po and o < pc:
            score += 2

        # 4. Bearish engulfing
        if c < o and pc > po and c < po and o > pc:
            score -= 2

        # 5. Doji
        if body_ratio < 0.1:
            score += 0  # neutral

        # 6. Strong bullish
        if c > o and body_ratio > 0.7:
            score += 1

        # 7. Strong bearish
        if c < o and body_ratio > 0.7:
            score -= 1

        entry = c

        if score >= 3:
            conf = Confidence.HIGH if abs(score) >= 4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Candle pattern score={score}: bullish patterns detected",
                invalidation=f"Close below {l:.4f}",
                bull_case=f"Score {score} bullish candle patterns aligned",
                bear_case="Score reversal would invalidate signal",
            )

        if score <= -3:
            conf = Confidence.HIGH if abs(score) >= 4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Candle pattern score={score}: bearish patterns detected",
                invalidation=f"Close above {h:.4f}",
                bull_case="Score reversal would invalidate signal",
                bear_case=f"Score {score} bearish candle patterns aligned",
            )

        return self._hold(df, f"Candle pattern score={score}: no strong signal")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is not None and len(df) >= 2:
            entry = float(df["close"].iloc[-2])
        else:
            entry = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
