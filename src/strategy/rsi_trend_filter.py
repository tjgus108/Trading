"""
RSITrendFilterStrategy:
- RSI14 (EWM Wilder method)
- RSI_SMA = RSI14.rolling(9).mean()
- BUY:  RSI14 > 50 AND RSI14 > RSI_SMA AND RSI crosses above 60 (prev<60, now>=60)
- SELL: RSI14 < 50 AND RSI14 < RSI_SMA AND RSI crosses below 40 (prev>40, now<=40)
- confidence: BUY시 RSI>65 → HIGH, SELL시 RSI<35 → HIGH, 그 외 MEDIUM
- 최소 행: 25
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_RSI_PERIOD = 14
_RSI_SMA_PERIOD = 9
_MIN_ROWS = 25


def _calc_rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    """EWM Wilder RSI."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta.clip(upper=0))
    alpha = 1.0 / period
    avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100.0 - (100.0 / (1.0 + rs))


class RSITrendFilterStrategy(BaseStrategy):
    name = "rsi_trend_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS + 2:
            return self._hold(df, "Insufficient data")

        # Use only completed candles
        completed = df.iloc[:-1]
        close = completed["close"]

        rsi14 = _calc_rsi_wilder(close, _RSI_PERIOD)
        rsi_sma = rsi14.rolling(_RSI_SMA_PERIOD).mean()

        # Last two completed candles
        last_rsi = float(rsi14.iloc[-1])
        prev_rsi = float(rsi14.iloc[-2])
        last_rsi_sma = float(rsi_sma.iloc[-1])
        last_close = float(close.iloc[-1])

        if np.isnan(last_rsi) or np.isnan(last_rsi_sma):
            return self._hold(df, "RSI NaN")

        context = (
            f"rsi14={last_rsi:.2f} prev_rsi={prev_rsi:.2f} "
            f"rsi_sma={last_rsi_sma:.2f} close={last_close:.2f}"
        )

        # BUY: RSI > 50 AND RSI > RSI_SMA AND cross above 60
        if last_rsi > 50 and last_rsi > last_rsi_sma and prev_rsi < 60 and last_rsi >= 60:
            confidence = Confidence.HIGH if last_rsi > 65 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"RSI trend filter BUY: RSI({last_rsi:.1f}) crossed above 60 "
                    f"with trend (>50 and >SMA {last_rsi_sma:.1f})"
                ),
                invalidation="RSI falls below 50 or drops below RSI_SMA",
                bull_case=context,
                bear_case=context,
            )

        # SELL: RSI < 50 AND RSI < RSI_SMA AND cross below 40
        if last_rsi < 50 and last_rsi < last_rsi_sma and prev_rsi > 40 and last_rsi <= 40:
            confidence = Confidence.HIGH if last_rsi < 35 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"RSI trend filter SELL: RSI({last_rsi:.1f}) crossed below 40 "
                    f"with downtrend (<50 and <SMA {last_rsi_sma:.1f})"
                ),
                invalidation="RSI rises above 50 or exceeds RSI_SMA",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
