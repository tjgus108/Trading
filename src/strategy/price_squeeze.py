"""
PriceSqueezeStrategy:
- Squeeze: BB upper < KC upper AND BB lower > KC lower
- Squeeze release: 이전봉 squeeze, 현재봉 not squeeze
- Momentum = close - close.rolling(5).mean()
- BUY:  squeeze_release AND momentum > 0
- SELL: squeeze_release AND momentum < 0
- confidence: HIGH if |momentum| > momentum.rolling(20).std() else MEDIUM
- 최소 데이터: 30행
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple

from .base import Action, BaseStrategy, Confidence, Signal

_BB_PERIOD = 20
_BB_STD = 2.0
_KC_PERIOD = 20
_KC_ATR_MULT = 1.5
_ATR_PERIOD = 14
_MOM_PERIOD = 5
_MOM_STD_PERIOD = 20
_MIN_ROWS = 30


class PriceSqueezeStrategy(BaseStrategy):
    name = "price_squeeze"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS + 2:
            return self._hold(df, "Insufficient data for price_squeeze (need 32+ rows)")

        close = df["close"].values
        high = df["high"].values
        low = df["low"].values
        n = len(close)

        # ── Bollinger Bands ──────────────────────────────────────────────
        bb_upper = np.full(n, np.nan)
        bb_lower = np.full(n, np.nan)
        for i in range(_BB_PERIOD - 1, n):
            w = close[i - _BB_PERIOD + 1: i + 1]
            m = float(np.mean(w))
            s = float(np.std(w, ddof=1))
            bb_upper[i] = m + _BB_STD * s
            bb_lower[i] = m - _BB_STD * s

        # ── EMA20 ────────────────────────────────────────────────────────
        ema20 = np.full(n, np.nan)
        ema20[_KC_PERIOD - 1] = float(np.mean(close[:_KC_PERIOD]))
        k = 2.0 / (_KC_PERIOD + 1)
        for i in range(_KC_PERIOD, n):
            ema20[i] = close[i] * k + ema20[i - 1] * (1 - k)

        # ── ATR14 ────────────────────────────────────────────────────────
        tr = np.zeros(n)
        for i in range(1, n):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
        atr14 = np.full(n, np.nan)
        if n >= _ATR_PERIOD:
            atr14[_ATR_PERIOD - 1] = float(np.mean(tr[1:_ATR_PERIOD]))
            for i in range(_ATR_PERIOD, n):
                atr14[i] = (atr14[i - 1] * (_ATR_PERIOD - 1) + tr[i]) / _ATR_PERIOD

        # ── Keltner Channel ──────────────────────────────────────────────
        kc_upper = np.where(np.isnan(ema20) | np.isnan(atr14), np.nan, ema20 + _KC_ATR_MULT * atr14)
        kc_lower = np.where(np.isnan(ema20) | np.isnan(atr14), np.nan, ema20 - _KC_ATR_MULT * atr14)

        # ── Squeeze ──────────────────────────────────────────────────────
        squeeze = np.zeros(n, dtype=bool)
        for i in range(n):
            if (not np.isnan(bb_upper[i]) and not np.isnan(kc_upper[i])
                    and not np.isnan(bb_lower[i]) and not np.isnan(kc_lower[i])):
                squeeze[i] = (bb_upper[i] < kc_upper[i]) and (bb_lower[i] > kc_lower[i])

        # ── Momentum = close - close.rolling(5).mean() ───────────────────
        momentum = np.full(n, np.nan)
        for i in range(_MOM_PERIOD - 1, n):
            momentum[i] = close[i] - float(np.mean(close[i - _MOM_PERIOD + 1: i + 1]))

        # ── Indices ──────────────────────────────────────────────────────
        idx = len(df) - 2  # last completed candle
        prev_idx = idx - 1

        if prev_idx < 0 or np.isnan(bb_upper[idx]) or np.isnan(kc_upper[idx]):
            return self._hold(df, "Insufficient data for indicators")

        prev_squeeze = bool(squeeze[prev_idx])
        curr_squeeze = bool(squeeze[idx])
        squeeze_release = prev_squeeze and not curr_squeeze

        last_close = float(close[idx])
        last_mom = float(momentum[idx]) if not np.isnan(momentum[idx]) else 0.0

        # Momentum std over last 20 bars
        mom_window = momentum[max(0, idx - _MOM_STD_PERIOD + 1): idx + 1]
        valid_mom = mom_window[~np.isnan(mom_window)]
        mom_std = float(np.std(valid_mom, ddof=1)) if len(valid_mom) >= 2 else 0.0

        context = (
            f"squeeze_release={squeeze_release} prev_squeeze={prev_squeeze} "
            f"curr_squeeze={curr_squeeze} momentum={last_mom:.4f} "
            f"mom_std={mom_std:.4f} close={last_close:.2f}"
        )

        if squeeze_release:
            high_conf = mom_std > 0 and abs(last_mom) > mom_std
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

            if last_mom > 0:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"Price squeeze released with bullish momentum "
                        f"(momentum={last_mom:.4f}>0)"
                    ),
                    invalidation="Momentum turns negative or squeeze re-forms",
                    bull_case=context,
                    bear_case=context,
                )

            if last_mom < 0:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"Price squeeze released with bearish momentum "
                        f"(momentum={last_mom:.4f}<0)"
                    ),
                    invalidation="Momentum turns positive or squeeze re-forms",
                    bull_case=context,
                    bear_case=context,
                )

        squeeze_status = "in_squeeze" if curr_squeeze else "no_squeeze"
        return self._hold(df, f"No squeeze release ({squeeze_status})", context, context)

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
