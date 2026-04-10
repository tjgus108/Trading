"""
LaguerreRSIStrategy: Ehlers Laguerre 필터 기반 RSI (0~1 범위).

BUY  : lrsi crosses above 0.2 (이전 < 0.2, 현재 >= 0.2)
SELL : lrsi crosses below 0.8 (이전 > 0.8, 현재 <= 0.8)
HOLD : 그 외
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


def _laguerre_rsi(close: pd.Series, gamma: float = 0.5) -> pd.Series:
    n = len(close)
    L0 = pd.Series(0.0, index=close.index)
    L1 = pd.Series(0.0, index=close.index)
    L2 = pd.Series(0.0, index=close.index)
    L3 = pd.Series(0.0, index=close.index)

    for i in range(1, n):
        c = float(close.iloc[i])
        l0_prev = float(L0.iloc[i - 1])
        l1_prev = float(L1.iloc[i - 1])
        l2_prev = float(L2.iloc[i - 1])
        l3_prev = float(L3.iloc[i - 1])

        L0.iloc[i] = (1 - gamma) * c + gamma * l0_prev
        L1.iloc[i] = -gamma * float(L0.iloc[i]) + l0_prev + gamma * l1_prev
        L2.iloc[i] = -gamma * float(L1.iloc[i]) + l1_prev + gamma * l2_prev
        L3.iloc[i] = -gamma * float(L2.iloc[i]) + l2_prev + gamma * l3_prev

    cu = pd.Series(0.0, index=close.index)
    cd = pd.Series(0.0, index=close.index)
    for i in range(n):
        l0 = float(L0.iloc[i])
        l1 = float(L1.iloc[i])
        l2 = float(L2.iloc[i])
        l3 = float(L3.iloc[i])
        cu_val = 0.0
        cd_val = 0.0
        if l0 >= l1:
            cu_val += l0 - l1
        else:
            cd_val += l1 - l0
        if l1 >= l2:
            cu_val += l1 - l2
        else:
            cd_val += l2 - l1
        if l2 >= l3:
            cu_val += l2 - l3
        else:
            cd_val += l3 - l2
        cu.iloc[i] = cu_val
        cd.iloc[i] = cd_val

    return cu / (cu + cd + 1e-10)


class LaguerreRSIStrategy(BaseStrategy):
    name = "laguerre_rsi"

    MIN_ROWS = 15
    GAMMA = 0.5
    BUY_LEVEL = 0.2
    SELL_LEVEL = 0.8

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"Insufficient data (minimum {self.MIN_ROWS} rows required)")

        idx = len(df) - 2
        lrsi = _laguerre_rsi(df["close"], self.GAMMA)

        lrsi_now = float(lrsi.iloc[idx])
        lrsi_prev = float(lrsi.iloc[idx - 1])

        if pd.isna(lrsi_now) or pd.isna(lrsi_prev):
            return self._hold(df, "NaN in Laguerre RSI")

        entry_price = float(df["close"].iloc[idx])

        cross_above_02 = lrsi_prev < self.BUY_LEVEL and lrsi_now >= self.BUY_LEVEL
        cross_below_08 = lrsi_prev > self.SELL_LEVEL and lrsi_now <= self.SELL_LEVEL

        if cross_above_02:
            confidence = Confidence.HIGH if lrsi_now < 0.1 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Laguerre RSI crossed above {self.BUY_LEVEL} "
                    f"(prev={lrsi_prev:.4f}, now={lrsi_now:.4f})"
                ),
                invalidation=f"Laguerre RSI crosses below {self.BUY_LEVEL}",
                bull_case="과매도 구간 탈출 — 반등 모멘텀",
                bear_case="fakeout 가능성",
            )

        if cross_below_08:
            confidence = Confidence.HIGH if lrsi_now > 0.9 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"Laguerre RSI crossed below {self.SELL_LEVEL} "
                    f"(prev={lrsi_prev:.4f}, now={lrsi_now:.4f})"
                ),
                invalidation=f"Laguerre RSI crosses above {self.SELL_LEVEL}",
                bull_case="fakeout 가능성",
                bear_case="과매수 구간 이탈 — 하락 전환",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=f"No cross — Laguerre RSI={lrsi_now:.4f}",
            invalidation="크로스 발생 시 재평가",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="N/A",
        )
