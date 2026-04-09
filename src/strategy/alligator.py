"""
Williams Alligator 전략.
- Jaw (Blue):   13기간 SMMA
- Teeth (Red):   8기간 SMMA
- Lips (Green):  5기간 SMMA
- SMMA: first = close[:period].mean(); 이후 = (prev*(period-1) + close_now) / period
- BUY:  lips > teeth > jaw AND close > lips
- SELL: lips < teeth < jaw AND close < lips
- confidence: 세 선 간격 > 전체 평균 간격 → HIGH
- 최소 행: 20
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20


def _smma(series: pd.Series, period: int) -> pd.Series:
    """Smoothed Moving Average (SMMA / RMA)."""
    result = np.full(len(series), np.nan)
    if len(series) < period:
        return pd.Series(result, index=series.index)
    result[period - 1] = float(series.iloc[:period].mean())
    for i in range(period, len(series)):
        result[i] = (result[i - 1] * (period - 1) + float(series.iloc[i])) / period
    return pd.Series(result, index=series.index)


class AlligatorStrategy(BaseStrategy):
    name = "alligator"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
            )

        close = df["close"]
        jaw = _smma(close, 13)
        teeth = _smma(close, 8)
        lips = _smma(close, 5)

        idx = len(df) - 2  # _last = iloc[-2]
        last_jaw = float(jaw.iloc[idx])
        last_teeth = float(teeth.iloc[idx])
        last_lips = float(lips.iloc[idx])
        entry = float(close.iloc[idx])

        if np.isnan(last_jaw) or np.isnan(last_teeth) or np.isnan(last_lips):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="SMMA 계산 데이터 부족",
                invalidation="",
            )

        # 정렬 조건
        bull_aligned = last_lips > last_teeth > last_jaw
        bear_aligned = last_lips < last_teeth < last_jaw

        # confidence: 세 선 간격 (lips-jaw) vs 전체 평균 간격
        lips_series = lips.dropna()
        jaw_series = jaw.reindex(lips_series.index)
        spread_series = (lips_series - jaw_series).abs()
        avg_spread = float(spread_series.mean()) if len(spread_series) > 0 else 0.0
        current_spread = abs(last_lips - last_jaw)
        high_conf = current_spread > avg_spread if avg_spread > 0 else False

        bull_case = (
            f"lips={last_lips:.4f} > teeth={last_teeth:.4f} > jaw={last_jaw:.4f}, "
            f"close={entry:.4f}"
        )
        bear_case = (
            f"lips={last_lips:.4f} < teeth={last_teeth:.4f} < jaw={last_jaw:.4f}, "
            f"close={entry:.4f}"
        )

        if bull_aligned and entry > last_lips:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Alligator eating upward: lips={last_lips:.4f} > teeth={last_teeth:.4f} "
                    f"> jaw={last_jaw:.4f}. close={entry:.4f} > lips."
                ),
                invalidation=f"close < lips ({last_lips:.4f}) or alignment breaks",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bear_aligned and entry < last_lips:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Alligator eating downward: lips={last_lips:.4f} < teeth={last_teeth:.4f} "
                    f"< jaw={last_jaw:.4f}. close={entry:.4f} < lips."
                ),
                invalidation=f"close > lips ({last_lips:.4f}) or alignment breaks",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reasons = []
        if bull_aligned and entry <= last_lips:
            reasons.append(f"Bull aligned but close={entry:.4f} <= lips={last_lips:.4f}")
        elif bear_aligned and entry >= last_lips:
            reasons.append(f"Bear aligned but close={entry:.4f} >= lips={last_lips:.4f}")
        else:
            reasons.append(
                f"No alignment. lips={last_lips:.4f} teeth={last_teeth:.4f} jaw={last_jaw:.4f}"
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="; ".join(reasons),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
