"""
Pin Bar (Rejection Candle) 전략:
- Bullish Pin Bar (BUY): 아래꼬리 >= 60%, 몸통 상단 33%, RSI14 < 50
- Bearish Pin Bar (SELL): 위꼬리 >= 60%, 몸통 하단 33%, RSI14 > 50
- confidence: HIGH if 꼬리 >= 70%, MEDIUM if >= 60%
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


class PinBarStrategy(BaseStrategy):
    name = "pin_bar"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        o = float(curr["open"])
        c = float(curr["close"])
        h = float(curr["high"])
        l = float(curr["low"])
        total_range = h - l

        rsi_val = float(_rsi(df["close"]).iloc[idx])

        if total_range <= 0:
            return self._hold(df, "Zero range candle")

        body_top = max(o, c)
        body_bottom = min(o, c)
        lower_wick = body_bottom - l
        upper_wick = h - body_top

        bullish_pin = (
            lower_wick > total_range * 0.6
            and (body_top + body_bottom) / 2 > l + total_range * 0.6
        )
        bearish_pin = (
            upper_wick > total_range * 0.6
            and (body_top + body_bottom) / 2 < l + total_range * 0.4
        )

        close_val = c

        if bullish_pin and rsi_val < 50:
            lower_ratio = lower_wick / total_range
            confidence = Confidence.HIGH if lower_ratio >= 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bullish Pin Bar: lower_wick={lower_ratio:.1%} RSI={rsi_val:.1f}",
                invalidation=f"Close below low ({l:.2f})",
                bull_case=f"Pin bar rejection at low: long lower wick ({lower_ratio:.1%}) shows buyer dominance",
                bear_case="",
            )

        if bearish_pin and rsi_val > 50:
            upper_ratio = upper_wick / total_range
            confidence = Confidence.HIGH if upper_ratio >= 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Bearish Pin Bar: upper_wick={upper_ratio:.1%} RSI={rsi_val:.1f}",
                invalidation=f"Close above high ({h:.2f})",
                bull_case="",
                bear_case=f"Pin bar rejection at high: long upper wick ({upper_ratio:.1%}) shows seller dominance",
            )

        return self._hold(
            df,
            f"No pin bar: lower_wick={lower_wick:.4f} upper_wick={upper_wick:.4f} "
            f"range={total_range:.4f} rsi={rsi_val:.1f}",
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
