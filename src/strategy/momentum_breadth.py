"""
MomentumBreadthStrategy:
- mom5 = close.pct_change(5)
- mom10 = close.pct_change(10)
- mom20 = close.pct_change(20)
- score = (mom5>0) + (mom10>0) + (mom20>0)  (0~3)
- BUY: score == 3
- SELL: score == 0
- confidence: HIGH if score==3 and mom5 > mom5.rolling(20).mean()*1.5 else MEDIUM
- 최소 35행 필요
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


class MomentumBreadthStrategy(BaseStrategy):
    name = "momentum_breadth"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for momentum_breadth",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        mom5 = df["close"].pct_change(5)
        mom10 = df["close"].pct_change(10)
        mom20 = df["close"].pct_change(20)
        mom5_avg = mom5.rolling(20).mean()

        v5 = mom5.iloc[idx]
        v10 = mom10.iloc[idx]
        v20 = mom20.iloc[idx]
        v5_avg = mom5_avg.iloc[idx]

        if pd.isna(v5) or pd.isna(v10) or pd.isna(v20):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for momentum_breadth (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        score = int(v5 > 0) + int(v10 > 0) + int(v20 > 0)
        entry = float(df["close"].iloc[idx])

        if score == 3:
            high_conf = (not pd.isna(v5_avg)) and (v5_avg != 0) and (v5 > v5_avg * 1.5)
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"모멘텀 breadth BUY: score=3, mom5={v5:.4f}, mom10={v10:.4f}, mom20={v20:.4f}",
                invalidation="score가 3 미만으로 하락 시",
                bull_case=f"모든 시간대 상승: score={score}",
                bear_case="모멘텀 과열 주의",
            )

        if score == 0:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"모멘텀 breadth SELL: score=0, mom5={v5:.4f}, mom10={v10:.4f}, mom20={v20:.4f}",
                invalidation="score가 1 이상으로 반등 시",
                bull_case="단순 과매도 조정 가능",
                bear_case=f"모든 시간대 하락: score={score}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"모멘텀 breadth HOLD: score={score}, mom5={v5:.4f}, mom10={v10:.4f}, mom20={v20:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
