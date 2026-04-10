"""
TailRiskFilterStrategy:
- 극단적 움직임(꼬리 리스크) 필터 후 안전한 진입
- BUY:  calm_period AND close > close_ma AND returns > 0
- SELL: calm_period AND close < close_ma AND returns < 0
- confidence: HIGH if calm_period AND z_score.abs() < 0.5 else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class TailRiskFilterStrategy(BaseStrategy):
    name = "tail_risk_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        idx = len(df) - 2

        returns = close.pct_change().fillna(0)
        return_std = returns.rolling(20, min_periods=1).std()
        z_score = returns / (return_std + 1e-10)
        extreme_move = (z_score.abs() > 2.5).astype(float)
        calm_period = extreme_move.rolling(5, min_periods=1).max() == 0
        close_ma = close.ewm(span=20, adjust=False).mean()

        calm = bool(calm_period.iloc[idx])
        ret = float(returns.iloc[idx])
        z = float(z_score.iloc[idx])
        price = float(close.iloc[idx])
        ma = float(close_ma.iloc[idx])

        if pd.isna(price) or pd.isna(ma) or pd.isna(ret) or pd.isna(z):
            return self._hold(df, "NaN values detected")

        context = f"close={price:.2f} ma={ma:.2f} ret={ret:.4f} z={z:.4f} calm={calm}"

        if calm and price > ma and ret > 0:
            confidence = Confidence.HIGH if abs(z) < 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"Calm period, uptrend: close({price:.2f})>ma({ma:.2f}), ret={ret:.4f}",
                invalidation=f"Extreme move (|z|>2.5) or close < MA ({ma:.2f})",
                bull_case=context,
                bear_case=context,
            )

        if calm and price < ma and ret < 0:
            confidence = Confidence.HIGH if abs(z) < 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"Calm period, downtrend: close({price:.2f})<ma({ma:.2f}), ret={ret:.4f}",
                invalidation=f"Extreme move (|z|>2.5) or close > MA ({ma:.2f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

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
