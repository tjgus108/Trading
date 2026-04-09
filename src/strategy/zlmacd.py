"""
ZeroLagMACDStrategy: Zero-Lag EMA 기반 MACD 전략.
- ZL EMA = ema + (ema - ema.ewm(span=period).mean())
- ZL MACD = zl_ema(12) - zl_ema(26)
- Signal = ZL MACD.ewm(span=9).mean()
- Histogram = ZL MACD - Signal
- BUY: Histogram 음→양 전환 AND ZL MACD > prev ZL MACD
- SELL: Histogram 양→음 전환 AND ZL MACD < prev ZL MACD
- 최소 행: 35
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


def _zl_ema(series: pd.Series, span: int) -> pd.Series:
    ema = series.ewm(span=span, adjust=False).mean()
    lag = ema.ewm(span=span, adjust=False).mean()
    return ema + (ema - lag)


class ZeroLagMACDStrategy(BaseStrategy):
    name = "zlmacd"

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
        last = self._last(df)
        entry = float(last["close"])

        zl12 = _zl_ema(close, 12)
        zl26 = _zl_ema(close, 26)
        zlmacd = zl12 - zl26
        signal_line = zlmacd.ewm(span=9, adjust=False).mean()
        histogram = zlmacd - signal_line

        prev_hist = float(histogram.iloc[-3])
        curr_hist = float(histogram.iloc[-2])
        prev_zl = float(zlmacd.iloc[-3])
        curr_zl = float(zlmacd.iloc[-2])

        # Confidence: |hist| > rolling(20) std
        hist_std = float(histogram.rolling(20).std().iloc[-2])
        high_conf = abs(curr_hist) > hist_std if hist_std > 0 else False
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        bull_case = (
            f"ZL MACD={curr_zl:.4f}, Hist={curr_hist:.4f} (prev={prev_hist:.4f}), "
            f"Hist_std={hist_std:.4f}"
        )
        bear_case = bull_case

        # BUY: histogram crosses above 0 AND ZL MACD rising
        if prev_hist < 0 and curr_hist >= 0 and curr_zl > prev_zl:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ZL MACD histogram crossed above 0 (prev={prev_hist:.4f} → now={curr_hist:.4f}). "
                    f"ZL MACD rising ({prev_zl:.4f} → {curr_zl:.4f})."
                ),
                invalidation=f"Histogram drops below 0 again",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: histogram crosses below 0 AND ZL MACD falling
        if prev_hist > 0 and curr_hist <= 0 and curr_zl < prev_zl:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ZL MACD histogram crossed below 0 (prev={prev_hist:.4f} → now={curr_hist:.4f}). "
                    f"ZL MACD falling ({prev_zl:.4f} → {curr_zl:.4f})."
                ),
                invalidation=f"Histogram rises above 0 again",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No histogram crossover. Hist={curr_hist:.4f}, ZL MACD={curr_zl:.4f}."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
