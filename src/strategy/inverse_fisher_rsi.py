"""
InverseFisherRSIStrategy:
- RSI(10) → wv = 0.1*(rsi-50) → ifr = (exp(2*wv)-1)/(exp(2*wv)+1)
- BUY:  ifr crosses above -0.5 (prev < -0.5, curr >= -0.5)
- SELL: ifr crosses below  0.5 (prev >  0.5, curr <=  0.5)
- confidence: HIGH if crossover strength |ifr-(-0.5)| > 0.3 (BUY) else MEDIUM
- 최소 데이터: 20행
"""

import math
import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_RSI_PERIOD = 10
_MIN_ROWS = 20
_BUY_THRESHOLD = -0.5
_SELL_THRESHOLD = 0.5
_HIGH_CONF_STRENGTH = 0.3


def _compute_rsi(close: np.ndarray, period: int = 10) -> np.ndarray:
    n = len(close)
    rsi = np.full(n, np.nan)
    if n < 2:
        return rsi

    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    # EWM with com=period-1 (alpha = 1/period)
    alpha = 1.0 / period
    avg_gain = np.full(n, np.nan)
    avg_loss = np.full(n, np.nan)
    avg_gain[0] = gain[0]
    avg_loss[0] = loss[0]
    for i in range(1, n):
        avg_gain[i] = gain[i] * alpha + avg_gain[i - 1] * (1 - alpha)
        avg_loss[i] = loss[i] * alpha + avg_loss[i - 1] * (1 - alpha)

    for i in range(n):
        if np.isnan(avg_gain[i]) or np.isnan(avg_loss[i]):
            continue
        if avg_loss[i] == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain[i] / avg_loss[i]
            rsi[i] = 100.0 - 100.0 / (1.0 + rs)

    return rsi


class InverseFisherRSIStrategy(BaseStrategy):
    name = "inverse_fisher_rsi"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS + 2:
            return self._hold(df, "Insufficient data for inverse_fisher_rsi (need 22+ rows)")

        close = df["close"].values
        n = len(close)

        # ── RSI(10) ──────────────────────────────────────────────────────
        rsi = _compute_rsi(close, _RSI_PERIOD)

        # ── Inverse Fisher Transform ─────────────────────────────────────
        ifr = np.full(n, np.nan)
        for i in range(n):
            if np.isnan(rsi[i]):
                continue
            wv = 0.1 * (rsi[i] - 50.0)
            exp2 = math.exp(2.0 * wv)
            ifr[i] = (exp2 - 1.0) / (exp2 + 1.0)

        # ── Indices ──────────────────────────────────────────────────────
        idx = len(df) - 2  # last completed candle
        prev_idx = idx - 1

        if prev_idx < 0 or np.isnan(ifr[idx]) or np.isnan(ifr[prev_idx]):
            return self._hold(df, "Insufficient data for IFR indicator")

        last_close = float(close[idx])
        curr_ifr = float(ifr[idx])
        prev_ifr = float(ifr[prev_idx])

        # ── Crossover signals ────────────────────────────────────────────
        buy_cross = prev_ifr < _BUY_THRESHOLD and curr_ifr >= _BUY_THRESHOLD
        sell_cross = prev_ifr > _SELL_THRESHOLD and curr_ifr <= _SELL_THRESHOLD

        context = (
            f"ifr={curr_ifr:.4f} prev_ifr={prev_ifr:.4f} "
            f"rsi={rsi[idx]:.2f} close={last_close:.2f}"
        )

        if buy_cross:
            strength = abs(curr_ifr - _BUY_THRESHOLD)
            confidence = Confidence.HIGH if strength > _HIGH_CONF_STRENGTH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"IFR crossed above {_BUY_THRESHOLD} "
                    f"(prev={prev_ifr:.4f} → curr={curr_ifr:.4f})"
                ),
                invalidation=f"IFR drops back below {_BUY_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        if sell_cross:
            strength = abs(curr_ifr - _SELL_THRESHOLD)
            confidence = Confidence.HIGH if strength > _HIGH_CONF_STRENGTH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"IFR crossed below {_SELL_THRESHOLD} "
                    f"(prev={prev_ifr:.4f} → curr={curr_ifr:.4f})"
                ),
                invalidation=f"IFR rises back above {_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No IFR crossover (ifr={curr_ifr:.4f})", context, context)

    def _hold(self, df: Optional[pd.DataFrame], reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
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
