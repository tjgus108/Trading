"""
RSI Divergence 전략:
- Bearish Divergence: price higher high + RSI lower high → SELL
- Bullish Divergence: price lower low + RSI higher low → BUY
- Lookback: 5~15 candles
- Confidence: HIGH if divergence > 2%, MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_LOOKBACK_MIN = 5
_LOOKBACK_MAX = 15
_HIGH_CONF_THRESHOLD = 0.02  # 2%


class RsiDivergenceStrategy(BaseStrategy):
    name = "rsi_divergence"

    def generate(self, df: pd.DataFrame) -> Signal:
        # Need at least LOOKBACK_MAX + 2 rows
        if df is None or len(df) < _LOOKBACK_MAX + 2:
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
        rsi = last["rsi14"]

        # Window: rows from index -(LOOKBACK_MAX+2) to -2 (inclusive), i.e. the lookback window
        window = df.iloc[-(  _LOOKBACK_MAX + 2): -1]  # includes last candle

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
                invalidation=f"Close below recent swing low",
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
                invalidation=f"Close above recent swing high",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, "No divergence detected", bull_case, bear_case)

    # ── Divergence detection ─────────────────────────────────────────────

    def _check_bearish_divergence(self, window: pd.DataFrame) -> tuple[bool, float]:
        """
        price: higher high (current > earlier high)
        rsi:   lower high  (current rsi < earlier rsi at that high)
        Returns (detected, divergence_pct)
        """
        last_row = window.iloc[-1]
        earlier = window.iloc[:-1]

        price_high_now = last_row["high"]
        rsi_now = last_row["rsi14"]

        # Find an earlier swing high that is lower in price but higher in RSI
        for i in range(len(earlier) - 1, max(len(earlier) - _LOOKBACK_MAX, -1), -1):
            row = earlier.iloc[i]
            price_ref = row["high"]
            rsi_ref = row["rsi14"]

            if price_high_now > price_ref and rsi_now < rsi_ref:
                price_div = (price_high_now - price_ref) / price_ref
                rsi_div = (rsi_ref - rsi_now) / rsi_ref
                div_pct = (price_div + rsi_div) / 2
                return True, div_pct

        return False, 0.0

    def _check_bullish_divergence(self, window: pd.DataFrame) -> tuple[bool, float]:
        """
        price: lower low  (current < earlier low)
        rsi:   higher low (current rsi > earlier rsi at that low)
        Returns (detected, divergence_pct)
        """
        last_row = window.iloc[-1]
        earlier = window.iloc[:-1]

        price_low_now = last_row["low"]
        rsi_now = last_row["rsi14"]

        for i in range(len(earlier) - 1, max(len(earlier) - _LOOKBACK_MAX, -1), -1):
            row = earlier.iloc[i]
            price_ref = row["low"]
            rsi_ref = row["rsi14"]

            if price_low_now < price_ref and rsi_now > rsi_ref:
                price_div = (price_ref - price_low_now) / price_ref
                rsi_div = (rsi_now - rsi_ref) / rsi_now if rsi_now != 0 else 0
                div_pct = (price_div + rsi_div) / 2
                return True, div_pct

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
