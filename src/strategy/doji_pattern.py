"""
Doji Candle Pattern 전략:
- Doji 정의: body < total_range * 0.1
- BUY: 현재봉 Doji + 이전봉 큰 음봉(body > ATR*0.5) + RSI14 < 45
- SELL: 현재봉 Doji + 이전봉 큰 양봉(body > ATR*0.5) + RSI14 > 55
- confidence: HIGH if body < range*0.05 (완벽한 Doji), MEDIUM otherwise
- 최소 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class DojiPatternStrategy(BaseStrategy):
    name = "doji_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]
        atr = float(df["atr14"].iloc[idx])

        body_curr = abs(float(curr["close"]) - float(curr["open"]))
        range_curr = float(curr["high"]) - float(curr["low"])
        is_doji = range_curr > 0 and body_curr < range_curr * 0.1

        body_prev = abs(float(prev["close"]) - float(prev["open"]))
        prev_bearish = float(prev["open"]) > float(prev["close"]) and body_prev > atr * 0.5
        prev_bullish = float(prev["close"]) > float(prev["open"]) and body_prev > atr * 0.5

        rsi_val = float(_rsi(df["close"]).iloc[idx])

        close = float(curr["close"])

        if not is_doji:
            return self._hold(df, f"No Doji: body={body_curr:.4f} range={range_curr:.4f} rsi={rsi_val:.1f}")

        confidence = Confidence.HIGH if range_curr > 0 and body_curr < range_curr * 0.05 else Confidence.MEDIUM

        if prev_bearish and rsi_val < 45:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Doji after bearish candle, RSI={rsi_val:.1f}",
                invalidation=f"Close below low ({float(curr['low']):.2f})",
                bull_case=f"Doji reversal after strong bearish candle",
                bear_case="",
            )

        if prev_bullish and rsi_val > 55:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Doji after bullish candle, RSI={rsi_val:.1f}",
                invalidation=f"Close above high ({float(curr['high']):.2f})",
                bull_case="",
                bear_case=f"Doji reversal after strong bullish candle",
            )

        return self._hold(df, f"Doji but no reversal condition: rsi={rsi_val:.1f} prev_bearish={prev_bearish} prev_bullish={prev_bullish}")

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
