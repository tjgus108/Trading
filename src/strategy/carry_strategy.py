"""
CarryStrategy: 가격 캐리(내재 자본 비용) 대리 지표 기반
- BUY:  z_carry > 1.5 AND carry_proxy > 0 AND carry_proxy > carry_ma
- SELL: z_carry < -1.5 AND carry_proxy < 0 AND carry_proxy < carry_ma
- confidence: HIGH if abs(z_carry) > 2.0 else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class CarryStrategy(BaseStrategy):
    name = "carry_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        carry_proxy = close / close.shift(1) - 1
        carry_ma = carry_proxy.rolling(20, min_periods=1).mean()
        carry_std = carry_proxy.rolling(20, min_periods=1).std()
        z_carry = (carry_proxy - carry_ma) / (carry_std + 1e-10)

        idx = len(df) - 2
        last = df.iloc[idx]

        cp = carry_proxy.iloc[idx]
        cm = carry_ma.iloc[idx]
        zc = z_carry.iloc[idx]

        if any(pd.isna(v) for v in [cp, cm, zc]):
            return self._hold(df, "NaN in indicators")

        close_val = float(last["close"])
        context = f"carry_proxy={cp:.4f} carry_ma={cm:.4f} z_carry={zc:.4f}"

        if zc > 1.5 and cp > 0 and cp > cm:
            confidence = Confidence.HIGH if abs(zc) > 2.0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Carry BUY: z_carry={zc:.4f}>1.5, carry_proxy={cp:.4f}>0 and >carry_ma={cm:.4f}",
                invalidation="z_carry drops below 1.5 or carry_proxy turns negative",
                bull_case=context,
                bear_case=context,
            )

        if zc < -1.5 and cp < 0 and cp < cm:
            confidence = Confidence.HIGH if abs(zc) > 2.0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Carry SELL: z_carry={zc:.4f}<-1.5, carry_proxy={cp:.4f}<0 and <carry_ma={cm:.4f}",
                invalidation="z_carry rises above -1.5 or carry_proxy turns positive",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No carry signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close_val = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
