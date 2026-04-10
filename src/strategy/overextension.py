"""
OverextensionStrategy — 추세 과신장 후 복귀 감지.

- distance_from_ema = (close - EMA50) / EMA50 * 100  (%)
- dist_std = distance_from_ema.rolling(20).std()
- Overextended up:   distance_from_ema > dist_std * 2
- Overextended down: distance_from_ema < -dist_std * 2

BUY:  overextended_down AND close > close.shift(1)  (복귀 시작)
SELL: overextended_up   AND close < close.shift(1)  (복귀 시작)
HOLD: 그 외

confidence:
  HIGH   if |distance| > dist_std * 3
  MEDIUM otherwise

최소 데이터: 75행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 75


class OverextensionStrategy(BaseStrategy):
    name = "overextension"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for Overextension (need 75 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]

        ema50 = df["close"].ewm(span=50, adjust=False).mean()
        distance_from_ema = (df["close"] - ema50) / ema50 * 100
        dist_std = distance_from_ema.rolling(20).std()

        dist_now = float(distance_from_ema.iloc[idx])
        std_now = float(dist_std.iloc[idx])
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])

        if std_now == 0:
            return self._hold(df, "dist_std=0, cannot compute overextension")

        overextended_up = dist_now > std_now * 2
        overextended_down = dist_now < -std_now * 2
        close_rising = close_now > close_prev
        close_falling = close_now < close_prev

        high_conf = abs(dist_now) > std_now * 3

        context = (
            f"close={close_now:.4f} dist={dist_now:.4f}% std={std_now:.4f}% "
            f"2σ={std_now * 2:.4f}%"
        )

        # BUY 조건
        if overextended_down and close_rising:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Overextension BUY: 과매도 구간({dist_now:.2f}% < -{std_now * 2:.2f}%), "
                    f"복귀 시작(close {close_prev:.4f}→{close_now:.4f})"
                ),
                invalidation="distance 추가 확대 또는 close 다시 하락",
                bull_case=context,
                bear_case=context,
            )

        # SELL 조건
        if overextended_up and close_falling:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Overextension SELL: 과매수 구간({dist_now:.2f}% > {std_now * 2:.2f}%), "
                    f"복귀 시작(close {close_prev:.4f}→{close_now:.4f})"
                ),
                invalidation="distance 추가 확대 또는 close 다시 상승",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: dist={dist_now:.4f}% 2σ±{std_now * 2:.4f}%",
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
