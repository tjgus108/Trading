"""
TrendMomentumScoreStrategy:
- EMA 정렬 기반 trend_score + ROC 기반 mom_score 합산
- total_bull >= 4 → BUY, total_bull <= 1 → SELL
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class TrendMomentumScoreStrategy(BaseStrategy):
    name = "trend_momentum_score"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]

        # Trend score
        ema10 = close.ewm(span=10, adjust=False).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()
        trend_score = (
            (close > ema10).astype(int)
            + (ema10 > ema20).astype(int)
            + (ema20 > ema50).astype(int)
        )

        # Momentum score
        roc5 = close.pct_change(5)
        roc10 = close.pct_change(10)
        mom_score = (roc5 > 0).astype(int) + (roc10 > 0).astype(int)

        total_bull = trend_score + mom_score  # 0~5
        total_bear = 5 - total_bull

        idx = len(df) - 2
        last = self._last(df)
        entry = float(last["close"])

        bull_val = int(total_bull.iloc[idx])
        bear_val = int(total_bear.iloc[idx])

        # NaN 체크
        if pd.isna(total_bull.iloc[idx]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 NaN",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        bull_case = f"total_bull={bull_val}"
        bear_case = f"total_bear={bear_val}"

        if bull_val >= 4:
            conf = Confidence.HIGH if bull_val == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"강한 상승 추세+모멘텀: total_bull={bull_val}",
                invalidation="EMA 정렬 붕괴",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bull_val <= 1:
            conf = Confidence.HIGH if bull_val == 0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"강한 하락 추세+모멘텀: total_bull={bull_val}",
                invalidation="EMA 정렬 회복",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"중립 구간: total_bull={bull_val}",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
