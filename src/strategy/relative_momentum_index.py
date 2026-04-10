"""
RelativeMomentumIndexStrategy:
- RMI (RSI의 변형: 1봉 변화 대신 N봉 변화 사용)
- BUY: rmi < 30 AND rmi > rmi.shift(1) (과매도 반등)
- SELL: rmi > 70 AND rmi < rmi.shift(1) (과매수 하락)
"""

import math

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MOMENTUM_PERIOD = 3
_RMI_PERIOD = 14


class RelativeMomentumIndexStrategy(BaseStrategy):
    name = "relative_momentum_index"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 20:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        idx = len(df) - 2

        delta = close.diff(_MOMENTUM_PERIOD)
        gain = delta.clip(lower=0).rolling(_RMI_PERIOD, min_periods=1).mean()
        loss = (-delta.clip(upper=0)).rolling(_RMI_PERIOD, min_periods=1).mean()
        rmi = 100 - 100 / (1 + gain / (loss + 1e-10))
        rmi_ma = rmi.rolling(5, min_periods=1).mean()

        last_rmi = rmi.iloc[idx]
        prev_rmi = rmi.iloc[idx - 1] if idx >= 1 else float("nan")
        last_close = close.iloc[idx]

        if any(math.isnan(v) for v in [last_rmi, prev_rmi, last_close]):
            return self._hold(df, "NaN in RMI indicators")

        if last_rmi < 30 and last_rmi > prev_rmi:
            conf = Confidence.HIGH if last_rmi < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=(
                    f"RMI oversold bounce: rmi={last_rmi:.2f} < 30, "
                    f"rising from {prev_rmi:.2f}"
                ),
                invalidation=f"RMI falls back below {last_rmi:.2f}",
                bull_case=f"RMI={last_rmi:.2f} prev={prev_rmi:.2f}",
                bear_case="",
            )

        if last_rmi > 70 and last_rmi < prev_rmi:
            conf = Confidence.HIGH if last_rmi > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=(
                    f"RMI overbought reversal: rmi={last_rmi:.2f} > 70, "
                    f"falling from {prev_rmi:.2f}"
                ),
                invalidation=f"RMI rises back above {last_rmi:.2f}",
                bull_case="",
                bear_case=f"RMI={last_rmi:.2f} prev={prev_rmi:.2f}",
            )

        return self._hold(
            df,
            f"No RMI signal (rmi={last_rmi:.2f}, prev={prev_rmi:.2f})",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
