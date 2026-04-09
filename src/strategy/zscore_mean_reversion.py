"""
Z-Score Mean Reversion 전략:
- BUY:  Z-Score < -2.0 (2 표준편차 아래, 과매도)
- SELL: Z-Score > 2.0  (2 표준편차 위, 과매수)
- HOLD: -2.0 <= Z-Score <= 2.0
- confidence: HIGH if |Z-Score| > 2.5, MEDIUM if |Z-Score| > 2.0
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 20
_BUY_THRESHOLD = -2.0
_SELL_THRESHOLD = 2.0
_HIGH_CONF_ABS = 2.5


class ZScoreMeanReversionStrategy(BaseStrategy):
    name = "zscore_mean_reversion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        period = _PERIOD
        rolling_mean = df["close"].rolling(period).mean()
        rolling_std = df["close"].rolling(period).std()
        zscore = (df["close"] - rolling_mean) / rolling_std.replace(0, 1e-10)

        idx = len(df) - 2
        z_now = float(zscore.iloc[idx])
        close_now = float(df["close"].iloc[idx])

        context = f"close={close_now:.2f} zscore={z_now:.4f}"

        if z_now < _BUY_THRESHOLD:
            confidence = Confidence.HIGH if abs(z_now) > _HIGH_CONF_ABS else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"Z-Score 과매도: z={z_now:.4f}<{_BUY_THRESHOLD} (2 표준편차 아래)",
                invalidation=f"Z-Score >= {_BUY_THRESHOLD}",
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
                reasoning=f"Z-Score 과매수: z={z_now:.4f}>{_SELL_THRESHOLD} (2 표준편차 위)",
                invalidation=f"Z-Score <= {_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: zscore={z_now:.4f}", context, context)

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
