"""
BullBearPowerStrategy — Elder's Bull Bear Power.

- EMA13 계산
- Bull Power = high - EMA13
- Bear Power = low - EMA13

BUY:  Bear Power < 0 AND Bear Power rising (bear_now > bear_prev) AND EMA13 rising
SELL: Bull Power > 0 AND Bull Power falling (bull_now < bull_prev) AND EMA13 falling
HOLD: 그 외

confidence:
  HIGH   if |Bear Power| > EMA13 * 0.01 (BUY) or |Bull Power| > EMA13 * 0.01 (SELL)
  MEDIUM otherwise

최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class BullBearPowerStrategy(BaseStrategy):
    name = "bull_bear_power"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for BullBearPower (need 20 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]

        ema13 = df["close"].ewm(span=13, adjust=False).mean()
        bull_power = df["high"] - ema13
        bear_power = df["low"] - ema13

        ema_now = float(ema13.iloc[idx])
        ema_prev = float(ema13.iloc[idx - 1])
        bull_now = float(bull_power.iloc[idx])
        bull_prev = float(bull_power.iloc[idx - 1])
        bear_now = float(bear_power.iloc[idx])
        bear_prev = float(bear_power.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        threshold = abs(ema_now) * 0.01

        context = (
            f"close={close:.4f} ema13={ema_now:.4f} "
            f"bull={bull_now:.4f} bear={bear_now:.4f}"
        )

        # BUY 조건
        ema_rising = ema_now > ema_prev
        bear_negative = bear_now < 0
        bear_rising = bear_now > bear_prev

        if ema_rising and bear_negative and bear_rising:
            confidence = (
                Confidence.HIGH if abs(bear_now) > threshold else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"BullBearPower BUY: EMA13 상승({ema_prev:.4f}→{ema_now:.4f}), "
                    f"Bear Power<0({bear_now:.4f}), 상승 중({bear_prev:.4f}→{bear_now:.4f})"
                ),
                invalidation="EMA13 하락 전환 또는 Bear Power 악화",
                bull_case=context,
                bear_case=context,
            )

        # SELL 조건
        ema_falling = ema_now < ema_prev
        bull_positive = bull_now > 0
        bull_falling = bull_now < bull_prev

        if ema_falling and bull_positive and bull_falling:
            confidence = (
                Confidence.HIGH if abs(bull_now) > threshold else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"BullBearPower SELL: EMA13 하락({ema_prev:.4f}→{ema_now:.4f}), "
                    f"Bull Power>0({bull_now:.4f}), 하락 중({bull_prev:.4f}→{bull_now:.4f})"
                ),
                invalidation="EMA13 상승 전환 또는 Bull Power 증가",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: ema_up={ema_rising} bear={bear_now:.4f} bull={bull_now:.4f}",
            context,
            context,
        )

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
