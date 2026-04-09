"""
BBBandwidthStrategy: Bollinger Bandwidth Squeeze 전략.
밴드 폭 수축 + 상방/하방 돌파 예상 → BUY/SELL
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 45


class BBBandwidthStrategy(BaseStrategy):
    name = "bb_bandwidth"

    def __init__(self, bb_period: int = 20, std_mult: float = 2.0, bw_period: int = 20):
        self.bb_period = bb_period
        self.std_mult = std_mult
        self.bw_period = bw_period

    def _calc_bands(self, df: pd.DataFrame):
        close = df["close"]
        sma = close.rolling(self.bb_period).mean()
        std = close.rolling(self.bb_period).std(ddof=0)
        upper = sma + self.std_mult * std
        lower = sma - self.std_mult * std
        bandwidth = (upper - lower) / sma
        bw_sma = bandwidth.rolling(self.bw_period).mean()
        return sma, upper, lower, bandwidth, bw_sma

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"데이터 부족: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        sma, upper, lower, bandwidth, bw_sma = self._calc_bands(df)

        last = self._last(df)  # iloc[-2]
        idx = df.index[-2]

        close_val = float(last["close"])
        bw_val = float(bandwidth.loc[idx])
        bw_sma_val = float(bw_sma.loc[idx])
        upper_val = float(upper.loc[idx])
        lower_val = float(lower.loc[idx])

        if pd.isna(bw_val) or pd.isna(bw_sma_val) or bw_sma_val == 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="지표 계산 불가 (NaN)",
                invalidation="",
            )

        # Squeeze: bandwidth < BW_SMA * 0.7
        squeezed = bw_val < bw_sma_val * 0.7

        # Confidence
        extreme_squeeze = bw_val < bw_sma_val * 0.5

        if squeezed and close_val > upper_val * 0.99:
            conf = Confidence.HIGH if extreme_squeeze else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"BB 수축(BW={bw_val:.4f}, BW_SMA={bw_sma_val:.4f}) + 상단 근접 돌파 예상",
                invalidation="밴드 확장 후 close가 upper 하회 시 무효",
                bull_case="수축 후 상방 에너지 방출 예상.",
                bear_case="하방 돌파 가능성 존재.",
            )

        if squeezed and close_val < lower_val * 1.01:
            conf = Confidence.HIGH if extreme_squeeze else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"BB 수축(BW={bw_val:.4f}, BW_SMA={bw_sma_val:.4f}) + 하단 근접 돌파 예상",
                invalidation="밴드 확장 후 close가 lower 상회 시 무효",
                bull_case="반등 가능성 존재.",
                bear_case="수축 후 하방 에너지 방출 예상.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"조건 미충족: BW={bw_val:.4f}, BW_SMA={bw_sma_val:.4f}, squeezed={squeezed}",
            invalidation="",
        )
