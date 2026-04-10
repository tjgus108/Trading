"""
SpreadMomentumStrategy: EMA 스프레드 모멘텀.
두 EMA의 거리(스프레드) 변화율로 추세 강도를 측정한다.
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SpreadMomentumStrategy(BaseStrategy):
    name = "spread_momentum"

    _MIN_ROWS = 25

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < self._MIN_ROWS:
            price = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=price,
                reasoning="Insufficient data",
                invalidation="",
            )

        close = df["close"]

        ema_fast = close.ewm(span=8, adjust=False).mean()
        ema_slow = close.ewm(span=21, adjust=False).mean()
        spread = ema_fast - ema_slow
        spread_ma = spread.rolling(10, min_periods=1).mean()
        spread_roc = spread.diff(3)
        spread_roc_ma = spread_roc.rolling(5, min_periods=1).mean()
        spread_roc_std = spread_roc.rolling(20, min_periods=1).std()

        idx = len(df) - 2
        last = df.iloc[idx]
        entry = float(last["close"])

        s = spread.iloc[idx]
        s_roc = spread_roc.iloc[idx]
        s_roc_ma = spread_roc_ma.iloc[idx]
        s_roc_std = spread_roc_std.iloc[idx]
        s_ma = spread_ma.iloc[idx]

        # NaN 체크
        if any(math.isnan(v) for v in [s, s_roc, s_roc_ma]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in indicators",
                invalidation="",
            )

        # confidence
        if not math.isnan(s_roc_std) and s_roc_std > 0:
            confidence = Confidence.HIGH if abs(s_roc) > s_roc_std else Confidence.MEDIUM
        else:
            confidence = Confidence.MEDIUM

        bull_info = (
            f"spread={s:.6f} spread_ma={s_ma:.6f} "
            f"spread_roc={s_roc:.6f} spread_roc_ma={s_roc_ma:.6f}"
        )

        # BUY: 스프레드 양수 + 확대 중
        if s > 0 and s_roc > 0 and s_roc > s_roc_ma:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Spread expanding bullishly. {bull_info}",
                invalidation="spread turns negative or spread_roc falls below spread_roc_ma",
                bull_case="EMA fast > slow and spread momentum accelerating",
                bear_case="Spread compression or reversal",
            )

        # SELL: 스프레드 음수 + 확대 중
        if s < 0 and s_roc < 0 and s_roc < s_roc_ma:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Spread expanding bearishly. {bull_info}",
                invalidation="spread turns positive or spread_roc rises above spread_roc_ma",
                bull_case="Spread compression or reversal",
                bear_case="EMA fast < slow and spread momentum accelerating downward",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"No clear spread momentum. {bull_info}",
            invalidation="",
        )
