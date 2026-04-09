"""
Marubozu Pattern 전략:
- Marubozu: 꼬리가 없는 강한 추세 캔들
- Bullish Marubozu (BUY):
  - close > open (양봉)
  - body > ATR * 0.7
  - low > open - ATR * 0.05 (아래꼬리 없음)
  - high < close + ATR * 0.05 (위꼬리 없음)
- Bearish Marubozu (SELL):
  - close < open (음봉)
  - body > ATR * 0.7
  - high < open + ATR * 0.05 (위꼬리 없음)
  - low > close - ATR * 0.05 (아래꼬리 없음)
- confidence: HIGH if body > ATR * 1.0, MEDIUM otherwise
- 최소 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class MarubozuStrategy(BaseStrategy):
    name = "marubozu"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        atr = float(df["atr14"].iloc[idx])

        o = float(curr["open"])
        c = float(curr["close"])
        h = float(curr["high"])
        l = float(curr["low"])
        body = abs(c - o)
        tol = atr * 0.05

        bullish_maru = (
            c > o
            and body > atr * 0.7
            and l > o - tol
            and h < c + tol
        )
        bearish_maru = (
            c < o
            and body > atr * 0.7
            and h < o + tol
            and l > c - tol
        )

        if not bullish_maru and not bearish_maru:
            return self._hold(df, f"No Marubozu: body={body:.4f} atr={atr:.4f}")

        confidence = Confidence.HIGH if body > atr * 1.0 else Confidence.MEDIUM

        if bullish_maru:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"Bullish Marubozu: body={body:.4f} atr={atr:.4f}",
                invalidation=f"Close below low ({l:.2f})",
                bull_case="Strong bullish candle with no tails",
                bear_case="",
            )

        return Signal(
            action=Action.SELL,
            confidence=confidence,
            strategy=self.name,
            entry_price=c,
            reasoning=f"Bearish Marubozu: body={body:.4f} atr={atr:.4f}",
            invalidation=f"Close above high ({h:.2f})",
            bull_case="",
            bear_case="Strong bearish candle with no tails",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = df.iloc[len(df) - 2] if len(df) >= 2 else df.iloc[-1]
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
