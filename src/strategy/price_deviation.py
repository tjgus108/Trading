"""
PriceDeviationStrategy: SMA20 편차의 Z-Score 기반 평균 복귀 전략.
- BUY:  z_score < -1.5 (과매도, 평균 복귀 예상)
- SELL: z_score >  1.5 (과매수, 평균 복귀 예상)
- confidence: HIGH if |z_score| > 2.0
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_BUY_THRESHOLD = -1.5
_SELL_THRESHOLD = 1.5
_HIGH_CONF_ABS = 2.0


class PriceDeviationStrategy(BaseStrategy):
    name = "price_deviation"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        sma20 = df["close"].rolling(_PERIOD).mean()
        deviation = (df["close"] - sma20) / sma20 * 100
        dev_std = deviation.rolling(_PERIOD).std()
        z_score = deviation / dev_std.replace(0, 1e-10)

        row = self._last(df)
        idx = len(df) - 2
        z_now = float(z_score.iloc[idx])
        close_now = float(row["close"])

        context = f"close={close_now:.2f} z_score={z_now:.4f}"

        if z_now < _BUY_THRESHOLD:
            confidence = Confidence.HIGH if abs(z_now) > _HIGH_CONF_ABS else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"과매도: z={z_now:.4f}<{_BUY_THRESHOLD} (SMA20 하방 편차 과도)",
                invalidation=f"z_score >= {_BUY_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        if z_now > _SELL_THRESHOLD:
            confidence = Confidence.HIGH if abs(z_now) > _HIGH_CONF_ABS else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"과매수: z={z_now:.4f}>{_SELL_THRESHOLD} (SMA20 상방 편차 과도)",
                invalidation=f"z_score <= {_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: z_score={z_now:.4f}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        close = float(df["close"].iloc[idx])
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
