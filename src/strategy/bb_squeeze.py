"""
Bollinger Band Squeeze 전략:
- Squeeze: BB width < 30th percentile of last 50 bars
- Squeeze release + close > upper BB → BUY
- Squeeze release + close < lower BB → SELL
- BB period: 20, std: 2.0
- Volume confirmation: vol > 20-bar avg * 1.5 → HIGH, otherwise MEDIUM
- RSI filter: BUY blocked if rsi14 >= 75, SELL blocked if rsi14 <= 25
- HIGH confidence: vol_confirm AND (rsi14 < 60 for BUY, rsi14 > 40 for SELL)
"""

from typing import Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_BB_PERIOD = 20
_BB_STD = 2.0
_PERCENTILE_WINDOW = 50
_SQUEEZE_PERCENTILE = 30  # bottom 30% — 신호 빈도 증가 (기존 20%)
_VOL_WINDOW = 20
_VOL_MULTIPLIER = 1.5
_RSI_BUY_BLOCK = 75    # rsi >= 75이면 BUY 차단
_RSI_SELL_BLOCK = 25   # rsi <= 25이면 SELL 차단
_RSI_BUY_HIGH = 60     # rsi < 60이면 HIGH confidence (BUY)
_RSI_SELL_HIGH = 40    # rsi > 40이면 HIGH confidence (SELL)


class BbSqueezeStrategy(BaseStrategy):
    name = "bb_squeeze"

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = _BB_PERIOD + _PERCENTILE_WINDOW
        if len(df) < min_rows + 2:
            return self._hold(df, "Insufficient data")

        close = df["close"].values

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

        # Width percentile over past 50 bars (ending at prev candle)
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

        rsi = float(df["rsi14"].iloc[last_idx])

        # Volume confirmation
        vol = df["volume"].values[last_idx]
        vol_start = max(0, last_idx - _VOL_WINDOW)
        vol_ma = float(np.mean(df["volume"].values[vol_start:last_idx]))
        vol_confirm = bool(vol > vol_ma * _VOL_MULTIPLIER)

        bull_case = (
            f"BB width={last_width:.4f} threshold={squeeze_threshold:.4f} "
            f"close={last_close:.2f} upper={last_upper:.2f} "
            f"rsi14={rsi:.1f} vol_confirm={vol_confirm}"
        )
        bear_case = (
            f"BB width={last_width:.4f} threshold={squeeze_threshold:.4f} "
            f"close={last_close:.2f} lower={last_lower:.2f} "
            f"rsi14={rsi:.1f} vol_confirm={vol_confirm}"
        )

        if squeeze_released:
            if last_close > last_upper:
                # RSI 과매수 필터
                if rsi >= _RSI_BUY_BLOCK:
                    return self._hold(
                        df,
                        f"BB squeeze BUY blocked: rsi14={rsi:.1f} >= {_RSI_BUY_BLOCK}",
                        bull_case, bear_case,
                    )
                confidence = (
                    Confidence.HIGH
                    if vol_confirm and rsi < _RSI_BUY_HIGH
                    else Confidence.MEDIUM
                )
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"BB squeeze released, close ({last_close:.2f}) > upper BB ({last_upper:.2f}). "
                        f"Bullish momentum. rsi14={rsi:.1f} vol_confirm={vol_confirm}"
                    ),
                    invalidation=f"Close below BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if last_close < last_lower:
                # RSI 과매도 필터
                if rsi <= _RSI_SELL_BLOCK:
                    return self._hold(
                        df,
                        f"BB squeeze SELL blocked: rsi14={rsi:.1f} <= {_RSI_SELL_BLOCK}",
                        bull_case, bear_case,
                    )
                confidence = (
                    Confidence.HIGH
                    if vol_confirm and rsi > _RSI_SELL_HIGH
                    else Confidence.MEDIUM
                )
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"BB squeeze released, close ({last_close:.2f}) < lower BB ({last_lower:.2f}). "
                        f"Bearish momentum. rsi14={rsi:.1f} vol_confirm={vol_confirm}"
                    ),
                    invalidation=f"Close above BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            # Squeeze released, price inside bands — use mid as direction
            if last_close > last_mid:
                if rsi >= _RSI_BUY_BLOCK:
                    return self._hold(
                        df,
                        f"BB squeeze BUY (inside) blocked: rsi14={rsi:.1f} >= {_RSI_BUY_BLOCK}",
                        bull_case, bear_case,
                    )
                return Signal(
                    action=Action.BUY,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"BB squeeze released, close ({last_close:.2f}) > mid BB ({last_mid:.2f}) "
                        f"but inside bands. Mild bullish bias. rsi14={rsi:.1f}"
                    ),
                    invalidation=f"Close below BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if last_close < last_mid:
                if rsi <= _RSI_SELL_BLOCK:
                    return self._hold(
                        df,
                        f"BB squeeze SELL (inside) blocked: rsi14={rsi:.1f} <= {_RSI_SELL_BLOCK}",
                        bull_case, bear_case,
                    )
                return Signal(
                    action=Action.SELL,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=last_close,
                    reasoning=(
                        f"BB squeeze released, close ({last_close:.2f}) < mid BB ({last_mid:.2f}) "
                        f"but inside bands. Mild bearish bias. rsi14={rsi:.1f}"
                    ),
                    invalidation=f"Close above BB mid ({last_mid:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            # Exactly at mid — HOLD
            return self._hold(df, "Squeeze released but price at BB mid", bull_case, bear_case)

        squeeze_status = "in squeeze" if prev_in_squeeze else "no squeeze"
        return self._hold(df, f"No squeeze release ({squeeze_status})", bull_case, bear_case)

    # ── BB computation ───────────────────────────────────────────────────

    def _compute_bb(self, close: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
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
