"""
BBKeltnerSqueezeStrategy:
- Squeeze: BB (20, 2σ) 상하단이 Keltner Channel (20, 1.5×ATR) 내부에 있을 때
  BB upper < KC upper AND BB lower > KC lower → squeeze active
- Momentum = close - SMA(hl3, 20)  where hl3 = (high+low+close)/3
- BUY:  이전 squeeze AND 현재 돌파 (squeeze 해제) AND momentum > 0
- SELL: 이전 squeeze AND 현재 돌파 AND momentum < 0
- confidence: |momentum| > momentum.rolling(10).std() → HIGH, else MEDIUM
- 최소 행: 25
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple

from .base import Action, BaseStrategy, Confidence, Signal

_BB_PERIOD = 20
_BB_STD = 2.0
_KC_PERIOD = 20
_KC_ATR_MULT = 1.5
_ATR_PERIOD = 20
_MIN_ROWS = 25
_MOM_STD_PERIOD = 10


class BBKeltnerSqueezeStrategy(BaseStrategy):
    name = "bb_keltner_squeeze"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS + 2:
            return self._hold(df, "Insufficient data")

        # Use only completed candles (exclude last in-progress candle)
        completed = df.iloc[:-1]

        close = completed["close"].values
        high = completed["high"].values
        low = completed["low"].values

        n = len(close)

        # ── Bollinger Bands ──────────────────────────────────────────────
        bb_mid = np.full(n, np.nan)
        bb_upper = np.full(n, np.nan)
        bb_lower = np.full(n, np.nan)
        for i in range(_BB_PERIOD - 1, n):
            w = close[i - _BB_PERIOD + 1: i + 1]
            m = float(np.mean(w))
            s = float(np.std(w, ddof=1))
            bb_mid[i] = m
            bb_upper[i] = m + _BB_STD * s
            bb_lower[i] = m - _BB_STD * s

        # ── ATR (Wilder) ─────────────────────────────────────────────────
        tr = np.zeros(n)
        for i in range(1, n):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
        atr = np.full(n, np.nan)
        atr[_ATR_PERIOD - 1] = float(np.mean(tr[1:_ATR_PERIOD]))
        for i in range(_ATR_PERIOD, n):
            atr[i] = (atr[i - 1] * (_ATR_PERIOD - 1) + tr[i]) / _ATR_PERIOD

        # ── Keltner Channel ──────────────────────────────────────────────
        kc_mid = np.full(n, np.nan)
        kc_upper = np.full(n, np.nan)
        kc_lower = np.full(n, np.nan)
        for i in range(_KC_PERIOD - 1, n):
            w = close[i - _KC_PERIOD + 1: i + 1]
            kc_mid[i] = float(np.mean(w))
        kc_upper = np.where(np.isnan(kc_mid) | np.isnan(atr), np.nan, kc_mid + _KC_ATR_MULT * atr)
        kc_lower = np.where(np.isnan(kc_mid) | np.isnan(atr), np.nan, kc_mid - _KC_ATR_MULT * atr)

        # ── Squeeze detection ────────────────────────────────────────────
        squeeze = (bb_upper < kc_upper) & (bb_lower > kc_lower)

        # ── Momentum = close - SMA(hl3, 20) ─────────────────────────────
        hl3 = (high + low + close) / 3.0
        hl3_sma = np.full(n, np.nan)
        for i in range(_BB_PERIOD - 1, n):
            hl3_sma[i] = float(np.mean(hl3[i - _BB_PERIOD + 1: i + 1]))
        momentum = close - hl3_sma

        # ── Indices for last completed candle ────────────────────────────
        last_idx = n - 1   # last completed candle
        prev_idx = n - 2   # one before

        if prev_idx < _BB_PERIOD:
            return self._hold(df, "Insufficient data for indicators")

        prev_squeeze = bool(squeeze[prev_idx])
        curr_squeeze = bool(squeeze[last_idx])
        squeeze_released = prev_squeeze and not curr_squeeze

        last_close = float(close[last_idx])
        last_mom = float(momentum[last_idx])

        if np.isnan(last_mom):
            return self._hold(df, "Momentum NaN")

        # Momentum std over last 10 bars (ending at last_idx inclusive)
        mom_window_start = max(0, last_idx - _MOM_STD_PERIOD + 1)
        mom_window = momentum[mom_window_start: last_idx + 1]
        valid_mom = mom_window[~np.isnan(mom_window)]
        if len(valid_mom) >= 2:
            mom_std = float(np.std(valid_mom, ddof=1))
        else:
            mom_std = 0.0

        context = (
            f"squeeze={curr_squeeze} prev_squeeze={prev_squeeze} "
            f"momentum={last_mom:.4f} mom_std={mom_std:.4f} close={last_close:.2f}"
        )

        if squeeze_released:
            high_conf = mom_std > 0 and abs(last_mom) > mom_std
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

            if last_mom > 0:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"BB-Keltner squeeze released with bullish momentum "
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
                        f"BB-Keltner squeeze released with bearish momentum "
                        f"(momentum={last_mom:.4f}<0)"
                    ),
                    invalidation="Momentum turns positive or squeeze re-forms",
                    bull_case=context,
                    bear_case=context,
                )

        squeeze_status = "in_squeeze" if curr_squeeze else "no_squeeze"
        return self._hold(df, f"No squeeze release ({squeeze_status})", context, context)

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
