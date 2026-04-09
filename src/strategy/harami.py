"""
Harami (임산부) 캔들 패턴 반전 전략:
- Bullish Harami (BUY): 이전봉 큰 음봉 + 현재봉 작은 양봉 (이전봉 body 안에) + RSI14 < 50
- Bearish Harami (SELL): 이전봉 큰 양봉 + 현재봉 작은 음봉 (이전봉 body 안에) + RSI14 > 50
- confidence: HIGH if 현재봉 body < 이전봉 body * 0.3, MEDIUM otherwise
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


class HaramiStrategy(BaseStrategy):
    name = "harami"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]
        atr = float(df["atr14"].iloc[idx])
        rsi_val = float(_rsi(df["close"]).iloc[idx])

        prev_open = float(prev["open"])
        prev_close = float(prev["close"])
        curr_open = float(curr["open"])
        curr_close = float(curr["close"])

        prev_body = abs(prev_close - prev_open)
        curr_body = abs(curr_close - curr_open)
        prev_is_bearish = prev_open > prev_close
        prev_is_bullish = prev_close > prev_open
        curr_is_bullish = curr_close > curr_open
        curr_is_bearish = curr_close < curr_open

        prev_body_top = max(prev_open, prev_close)
        prev_body_bottom = min(prev_open, prev_close)
        inside = (
            curr_open < prev_body_top
            and curr_open > prev_body_bottom
            and curr_close < prev_body_top
            and curr_close > prev_body_bottom
        )

        close = curr_close

        # Bullish Harami
        if (
            prev_is_bearish
            and prev_body > atr * 0.5
            and curr_is_bullish
            and curr_body < prev_body * 0.5
            and inside
            and rsi_val < 50
        ):
            confidence = (
                Confidence.HIGH if curr_body < prev_body * 0.3 else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bullish Harami: prev_body={prev_body:.4f} curr_body={curr_body:.4f} RSI={rsi_val:.1f}",
                invalidation=f"Close below prev low ({float(prev['low']):.2f})",
                bull_case="Harami reversal after strong bearish candle",
                bear_case="",
            )

        # Bearish Harami
        if (
            prev_is_bullish
            and prev_body > atr * 0.5
            and curr_is_bearish
            and curr_body < prev_body * 0.5
            and inside
            and rsi_val > 50
        ):
            confidence = (
                Confidence.HIGH if curr_body < prev_body * 0.3 else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Bearish Harami: prev_body={prev_body:.4f} curr_body={curr_body:.4f} RSI={rsi_val:.1f}",
                invalidation=f"Close above prev high ({float(prev['high']):.2f})",
                bull_case="",
                bear_case="Harami reversal after strong bullish candle",
            )

        return self._hold(
            df,
            f"No Harami: prev_body={prev_body:.4f} curr_body={curr_body:.4f} inside={inside} rsi={rsi_val:.1f}",
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
