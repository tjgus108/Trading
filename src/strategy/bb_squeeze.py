"""
Bollinger Band Squeeze 전략:
- Squeeze: BB width < 20th percentile of last 50 bars
- Squeeze release + close > upper BB → BUY
- Squeeze release + close < lower BB → SELL
- BB period: 20, std: 2.0
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_BB_PERIOD = 20
_BB_STD = 2.0
_PERCENTILE_WINDOW = 50
_SQUEEZE_PERCENTILE = 20  # bottom 20%


class BbSqueezeStrategy(BaseStrategy):
    name = "bb_squeeze"

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = _BB_PERIOD + _PERCENTILE_WINDOW
        if len(df) < min_rows + 2:
            return self._hold(df, "Insufficient data")

        close = df["close"].values
        high = df["high"].values
        low = df["low"].values

        # Compute BB for all bars
        bb_mid, bb_upper, bb_lower, bb_width = self._compute_bb(close)

        # Use up to index -2 (last completed candle)
        last_idx = len(close) - 2

        # Current values (last completed candle)
        last_close = close[last_idx]
        last_upper = bb_upper[last_idx]
        last_lower = bb_lower[last_idx]
        last_mid = bb_mid[last_idx]
        last_width = bb_width[last_idx]

        # Previous candle: check if we were in squeeze
        prev_idx = last_idx - 1
        prev_width = bb_width[prev_idx]

        # Width percentile over past 50 bars (ending at prev candle, so squeeze window = bars before last)
        window_end = last_idx  # exclusive
        window_start = max(0, window_end - _PERCENTILE_WINDOW)
        width_window = bb_width[window_start:window_end]

        if len(width_window) < 10:
            return self._hold(df, "Insufficient width history")

        squeeze_threshold = float(np.percentile(width_window, _SQUEEZE_PERCENTILE))

        # Squeeze was active on previous candle
        prev_in_squeeze = prev_width <= squeeze_threshold
        # Squeeze released on current candle (width expanded above threshold)
        squeeze_released = prev_in_squeeze and last_width > squeeze_threshold

        rsi = df["rsi14"].iloc[last_idx]
        bull_case = f"BB width={last_width:.4f} threshold={squeeze_threshold:.4f} close={last_close:.2f} upper={last_upper:.2f}"
        bear_case = f"BB width={last_width:.4f} threshold={squeeze_threshold:.4f} close={last_close:.2f} lower={last_lower:.2f}"

        if squeeze_released:
            if last_close > last_upper:
                return Signal(
                    action=Action.BUY,
                    confidence=Confidence.HIGH,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=f"BB squeeze released, close ({last_close:.2f}) > upper BB ({last_upper:.2f}). Bullish momentum.",
                    invalidation=f"Close below BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if last_close < last_lower:
                return Signal(
                    action=Action.SELL,
                    confidence=Confidence.HIGH,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=f"BB squeeze released, close ({last_close:.2f}) < lower BB ({last_lower:.2f}). Bearish momentum.",
                    invalidation=f"Close above BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            # Squeeze released but price still inside bands — HOLD
            return self._hold(df, "Squeeze released but price inside bands", bull_case, bear_case)

        squeeze_status = "in squeeze" if prev_in_squeeze else "no squeeze"
        return self._hold(df, f"No squeeze release ({squeeze_status})", bull_case, bear_case)

    # ── BB computation ───────────────────────────────────────────────────

    def _compute_bb(self, close: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        n = len(close)
        mid = np.full(n, np.nan)
        upper = np.full(n, np.nan)
        lower = np.full(n, np.nan)

        for i in range(_BB_PERIOD - 1, n):
            window = close[i - _BB_PERIOD + 1: i + 1]
            m = float(np.mean(window))
            s = float(np.std(window, ddof=1))
            mid[i] = m
            upper[i] = m + _BB_STD * s
            lower[i] = m - _BB_STD * s

        width = np.where(np.isnan(mid), np.nan, (upper - lower) / mid)
        return mid, upper, lower, width

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=last["close"],
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
