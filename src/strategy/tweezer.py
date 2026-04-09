"""
Tweezer Pattern 전략:
- Tweezer Bottom (BUY): 이전봉 음봉 + 현재봉 양봉 + low 일치 + RSI14 < 50
- Tweezer Top (SELL): 이전봉 양봉 + 현재봉 음봉 + high 일치 + RSI14 > 50
- confidence: HIGH if 차이 < ATR*0.05, MEDIUM if < ATR*0.1
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


class TweezerStrategy(BaseStrategy):
    name = "tweezer"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]
        atr = float(df["atr14"].iloc[idx])
        rsi_val = float(_rsi(df["close"]).iloc[idx])

        curr_low = float(curr["low"])
        prev_low = float(prev["low"])
        curr_high = float(curr["high"])
        prev_high = float(prev["high"])

        low_match = abs(curr_low - prev_low) < atr * 0.1
        high_match = abs(curr_high - prev_high) < atr * 0.1

        prev_bearish = float(prev["close"]) < float(prev["open"])
        curr_bullish = float(curr["close"]) > float(curr["open"])
        prev_bullish = float(prev["close"]) > float(prev["open"])
        curr_bearish = float(curr["close"]) < float(curr["open"])

        close = float(curr["close"])

        # Tweezer Bottom (BUY)
        if prev_bearish and curr_bullish and low_match and rsi_val < 50:
            low_diff = abs(curr_low - prev_low)
            confidence = Confidence.HIGH if low_diff < atr * 0.05 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Tweezer Bottom: low_diff={low_diff:.4f} ATR={atr:.4f} RSI={rsi_val:.1f}",
                invalidation=f"Close below low ({curr_low:.2f})",
                bull_case="Tweezer Bottom reversal: matched lows indicate strong support",
                bear_case="",
            )

        # Tweezer Top (SELL)
        if prev_bullish and curr_bearish and high_match and rsi_val > 50:
            high_diff = abs(curr_high - prev_high)
            confidence = Confidence.HIGH if high_diff < atr * 0.05 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Tweezer Top: high_diff={high_diff:.4f} ATR={atr:.4f} RSI={rsi_val:.1f}",
                invalidation=f"Close above high ({curr_high:.2f})",
                bull_case="",
                bear_case="Tweezer Top reversal: matched highs indicate strong resistance",
            )

        return self._hold(
            df,
            f"No tweezer: low_match={low_match} high_match={high_match} "
            f"prev_bearish={prev_bearish} curr_bullish={curr_bullish} "
            f"prev_bullish={prev_bullish} curr_bearish={curr_bearish} rsi={rsi_val:.1f}",
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
