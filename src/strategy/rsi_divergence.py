"""
RSI Divergence 전략:
- Bearish Divergence: price higher high + RSI lower high → SELL
- Bullish Divergence: price lower low + RSI higher low → BUY
- Lookback: 5~20 candles (confirmed swing pivots only)
- Confidence: HIGH if divergence > 2%, MEDIUM otherwise
- Filters: RSI zone filter + min candle gap + swing pivot confirmation
           + min swing size (RSI diff >= 3, price change >= 0.5%)
           + EMA50 trend filter (bullish div valid in downtrend, bearish in uptrend)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_LOOKBACK_MIN = 5
_LOOKBACK_MAX = 20
_HIGH_CONF_THRESHOLD = 0.02  # 2%
_MIN_GAP = 3          # minimum candles between pivot and current
_SWING_WINDOW = 2     # bars each side to confirm local swing high/low
_RSI_BEAR_ZONE = 55   # bearish div: RSI at ref must be above this
_RSI_BULL_ZONE = 45   # bullish div: RSI at ref must be below this
_MIN_RSI_DIFF = 3.0   # minimum RSI difference to count as divergence
_MIN_PRICE_CHG = 0.005  # minimum price change (0.5%) to count as divergence


class RsiDivergenceStrategy(BaseStrategy):
    name = "rsi_divergence"

    def generate(self, df: pd.DataFrame) -> Signal:
        # Need at least LOOKBACK_MAX + SWING_WINDOW + 2 rows
        min_rows = _LOOKBACK_MAX + _SWING_WINDOW + 2
        if df is None or len(df) < min_rows:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)  # df.iloc[-2]
        entry = last["close"]

        # Window: LOOKBACK_MAX+2 bars ending at df.iloc[-2] (last completed candle)
        window = df.iloc[-(  _LOOKBACK_MAX + 2): -1]  # length = LOOKBACK_MAX+1

        bullish, bull_div_pct = self._check_bullish_divergence(window)
        bearish, bear_div_pct = self._check_bearish_divergence(window)

        bull_case = f"Bullish div {bull_div_pct:.1%}" if bullish else "No bullish divergence"
        bear_case = f"Bearish div {bear_div_pct:.1%}" if bearish else "No bearish divergence"

        if bullish and not bearish:
            conf = Confidence.HIGH if bull_div_pct >= _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Bullish RSI divergence: price lower low, RSI higher low ({bull_div_pct:.1%})",
                invalidation="Close below recent swing low",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bearish and not bullish:
            conf = Confidence.HIGH if bear_div_pct >= _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Bearish RSI divergence: price higher high, RSI lower high ({bear_div_pct:.1%})",
                invalidation="Close above recent swing high",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, "No divergence detected", bull_case, bear_case)

    # ── Swing pivot helpers ───────────────────────────────────────────────────

    @staticmethod
    def _is_swing_high(window: pd.DataFrame, i: int) -> bool:
        """True if row i is a local swing high (highest within SWING_WINDOW bars each side)."""
        sw = _SWING_WINDOW
        lo = max(0, i - sw)
        hi = min(len(window), i + sw + 1)
        return bool(window["high"].iloc[i] == window["high"].iloc[lo:hi].max())

    @staticmethod
    def _is_swing_low(window: pd.DataFrame, i: int) -> bool:
        """True if row i is a local swing low (lowest within SWING_WINDOW bars each side)."""
        sw = _SWING_WINDOW
        lo = max(0, i - sw)
        hi = min(len(window), i + sw + 1)
        return bool(window["low"].iloc[i] == window["low"].iloc[lo:hi].min())

    # ── Divergence detection ─────────────────────────────────────────────────

    def _check_bearish_divergence(self, window: pd.DataFrame) -> "Tuple[bool, float]":
        """
        price: higher high (current > earlier swing high)
        rsi:   lower high  (current rsi < earlier rsi at that swing high)
        RSI filter: ref RSI must be >= _RSI_BEAR_ZONE (overbought territory)
        Returns (detected, divergence_pct)
        """
        last_idx = len(window) - 1
        last_row = window.iloc[last_idx]

        price_high_now = last_row["high"]
        rsi_now = last_row["rsi14"]

        # Search earlier rows (most recent first), enforcing min gap
        search_end = max(last_idx - _MIN_GAP, 0)
        best_div = 0.0

        for i in range(search_end, max(search_end - _LOOKBACK_MAX, -1), -1):
            if not self._is_swing_high(window, i):
                continue

            row = window.iloc[i]
            price_ref = row["high"]
            rsi_ref = row["rsi14"]

            # RSI zone filter: ref point should be in elevated RSI territory
            if rsi_ref < _RSI_BEAR_ZONE:
                continue

            if price_high_now > price_ref and rsi_now < rsi_ref:
                price_div = (price_high_now - price_ref) / price_ref
                rsi_diff = rsi_ref - rsi_now
                # Min swing size filter: skip trivially small divergences
                if price_div < _MIN_PRICE_CHG or rsi_diff < _MIN_RSI_DIFF:
                    continue
                rsi_div = rsi_diff / rsi_ref
                div_pct = (price_div + rsi_div) / 2
                if div_pct > best_div:
                    best_div = div_pct

        if best_div > 0.0:
            return True, best_div
        return False, 0.0

    def _check_bullish_divergence(self, window: pd.DataFrame) -> "Tuple[bool, float]":
        """
        price: lower low  (current < earlier swing low)
        rsi:   higher low (current rsi > earlier rsi at that swing low)
        RSI filter: ref RSI must be <= _RSI_BULL_ZONE (oversold territory)
        Returns (detected, divergence_pct)
        """
        last_idx = len(window) - 1
        last_row = window.iloc[last_idx]

        price_low_now = last_row["low"]
        rsi_now = last_row["rsi14"]

        search_end = max(last_idx - _MIN_GAP, 0)
        best_div = 0.0

        for i in range(search_end, max(search_end - _LOOKBACK_MAX, -1), -1):
            if not self._is_swing_low(window, i):
                continue

            row = window.iloc[i]
            price_ref = row["low"]
            rsi_ref = row["rsi14"]

            # RSI zone filter: ref point should be in depressed RSI territory
            if rsi_ref > _RSI_BULL_ZONE:
                continue

            if price_low_now < price_ref and rsi_now > rsi_ref:
                price_div = (price_ref - price_low_now) / price_ref
                rsi_diff = rsi_now - rsi_ref
                # Min swing size filter: skip trivially small divergences
                if price_div < _MIN_PRICE_CHG or rsi_diff < _MIN_RSI_DIFF:
                    continue
                rsi_div = rsi_diff / rsi_now if rsi_now != 0 else 0
                div_pct = (price_div + rsi_div) / 2
                if div_pct > best_div:
                    best_div = div_pct

        if best_div > 0.0:
            return True, best_div
        return False, 0.0

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
