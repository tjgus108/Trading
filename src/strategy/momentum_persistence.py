"""
MomentumPersistenceStrategy: 모멘텀 지속성(autocorrelation) 활용 전략.
- BUY:  pos_streak >= 3 AND avg_return > 0 (3봉 이상 연속 상승 + 평균 상승 추세)
- SELL: neg_streak >= 3 AND avg_return < 0
- HOLD: 그 외
- confidence: HIGH if pos_streak >= 5 (BUY), HIGH if neg_streak >= 5 (SELL), else MEDIUM
- 최소 데이터: 25행
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_STREAK_BUY = 3
_STREAK_SELL = 3
_HIGH_STREAK = 5


class MomentumPersistenceStrategy(BaseStrategy):
    name = "momentum_persistence"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for momentum_persistence (need 25 rows)")

        close = df["close"]
        returns = close.pct_change()
        avg_return = returns.rolling(20).mean()

        idx = len(df) - 2

        avg_ret_val = float(avg_return.iloc[idx])
        if math.isnan(avg_ret_val):
            return self._hold(df, "Insufficient data for momentum_persistence (NaN in avg_return)")

        close_now = float(close.iloc[idx])

        # 연속 스트릭 계산 (최근 10봉)
        pos_streak = 0
        neg_streak = 0
        for i in range(idx - 9, idx + 1):
            if i < 0:
                continue
            r_raw = returns.iloc[i]
            r = float(r_raw) if not pd.isna(r_raw) else 0.0
            if r > 0:
                pos_streak += 1
                neg_streak = 0
            elif r < 0:
                neg_streak += 1
                pos_streak = 0
            else:
                pos_streak = 0
                neg_streak = 0

        context = (
            f"close={close_now:.2f} pos_streak={pos_streak} "
            f"neg_streak={neg_streak} avg_return={avg_ret_val:.6f}"
        )

        # BUY: 연속 상승 + 평균 상승 추세
        if pos_streak >= _STREAK_BUY and avg_ret_val > 0:
            confidence = Confidence.HIGH if pos_streak >= _HIGH_STREAK else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"모멘텀 지속: pos_streak={pos_streak}>={_STREAK_BUY} "
                    f"and avg_return={avg_ret_val:.6f}>0"
                ),
                invalidation=f"pos_streak < {_STREAK_BUY} or avg_return <= 0",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 연속 하락 + 평균 하락 추세
        if neg_streak >= _STREAK_SELL and avg_ret_val < 0:
            confidence = Confidence.HIGH if neg_streak >= _HIGH_STREAK else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"모멘텀 하락 지속: neg_streak={neg_streak}>={_STREAK_SELL} "
                    f"and avg_return={avg_ret_val:.6f}<0"
                ),
                invalidation=f"neg_streak < {_STREAK_SELL} or avg_return >= 0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: pos={pos_streak} neg={neg_streak}", context, context)

    def _hold(self, df: Optional[pd.DataFrame], reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) == 0:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
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
