"""
AdaptiveStopStrategy: ATR 기반 추적 손절 전략.
- ATR14 (EWM 방식)
- Long stop = close - multiplier * ATR14
- Short stop = close + multiplier * ATR14
- BUY: close > long_stop AND close > EMA50 AND RSI14 > 50
- SELL: close < short_stop AND close < EMA50 AND RSI14 < 50
- RSI: Wilder RSI (ewm span=14)
- confidence: RSI > 60 or RSI < 40 → HIGH
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


def _wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(span=period, adjust=False).mean()
    avg_loss = loss.ewm(span=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


class AdaptiveStopStrategy(BaseStrategy):
    name = "adaptive_stop"

    def __init__(self, multiplier: float = 2.0):
        self.multiplier = multiplier

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"Insufficient data: {len(df)} < {_MIN_ROWS}",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]

        # ATR14 (EWM)
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr14 = tr.ewm(span=14, adjust=False).mean()

        # EMA50
        ema50 = close.ewm(span=50, adjust=False).mean()

        # Wilder RSI14
        rsi14 = _wilder_rsi(close, 14)

        last = self._last(df)
        entry = float(last["close"])
        idx = -2

        curr_close = float(close.iloc[idx])
        curr_atr = float(atr14.iloc[idx])
        curr_ema50 = float(ema50.iloc[idx])
        curr_rsi = float(rsi14.iloc[idx])

        long_stop = curr_close - self.multiplier * curr_atr
        short_stop = curr_close + self.multiplier * curr_atr

        # Confidence
        high_conf = curr_rsi > 60 or curr_rsi < 40
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        bull_case = (
            f"Close={curr_close:.2f} > LongStop={long_stop:.2f}, "
            f"EMA50={curr_ema50:.2f}, RSI={curr_rsi:.1f}, ATR={curr_atr:.2f}"
        )
        bear_case = (
            f"Close={curr_close:.2f} < ShortStop={short_stop:.2f}, "
            f"EMA50={curr_ema50:.2f}, RSI={curr_rsi:.1f}, ATR={curr_atr:.2f}"
        )

        # BUY
        if curr_close > long_stop and curr_close > curr_ema50 and curr_rsi > 50:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Close ({curr_close:.2f}) > LongStop ({long_stop:.2f}), "
                    f"> EMA50 ({curr_ema50:.2f}), RSI={curr_rsi:.1f} > 50."
                ),
                invalidation=f"Close falls below long stop ({long_stop:.2f}) or EMA50 ({curr_ema50:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL
        if curr_close < short_stop and curr_close < curr_ema50 and curr_rsi < 50:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Close ({curr_close:.2f}) < ShortStop ({short_stop:.2f}), "
                    f"< EMA50 ({curr_ema50:.2f}), RSI={curr_rsi:.1f} < 50."
                ),
                invalidation=f"Close rises above short stop ({short_stop:.2f}) or EMA50 ({curr_ema50:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No clear trend signal. Close={curr_close:.2f}, EMA50={curr_ema50:.2f}, "
                f"RSI={curr_rsi:.1f}, LongStop={long_stop:.2f}, ShortStop={short_stop:.2f}."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
