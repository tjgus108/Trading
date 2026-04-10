"""
PriceActionQualityStrategy: 봉 품질 점수화 기반 전략.

- body_ratio > 0.6 AND 적은 wick → 강한 봉
- 연속 3봉 모두 강한 양봉 → BUY
- 연속 3봉 모두 강한 음봉 → SELL
- confidence: HIGH if body_ratio at idx > 0.8 else MEDIUM
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 10


class PriceActionQualityStrategy(BaseStrategy):
    name = "price_action_quality"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data for price_action_quality",
                invalidation="",
            )

        idx = len(df) - 2

        def _body_ratio(i: int) -> float:
            o = float(df["open"].iloc[i])
            c = float(df["close"].iloc[i])
            h = float(df["high"].iloc[i])
            lo = float(df["low"].iloc[i])
            total = max(h - lo, 0.0001)
            return abs(c - o) / total

        def _upper_wick_ratio(i: int) -> float:
            o = float(df["open"].iloc[i])
            c = float(df["close"].iloc[i])
            h = float(df["high"].iloc[i])
            lo = float(df["low"].iloc[i])
            total = max(h - lo, 0.0001)
            return (h - max(c, o)) / total

        def _lower_wick_ratio(i: int) -> float:
            o = float(df["open"].iloc[i])
            c = float(df["close"].iloc[i])
            h = float(df["high"].iloc[i])
            lo = float(df["low"].iloc[i])
            total = max(h - lo, 0.0001)
            return (min(c, o) - lo) / total

        last3_bull = all(
            float(df["close"].iloc[i]) > float(df["open"].iloc[i]) and
            (abs(float(df["close"].iloc[i]) - float(df["open"].iloc[i])) /
             max(float(df["high"].iloc[i]) - float(df["low"].iloc[i]), 0.0001)) > 0.6
            for i in range(idx - 2, idx + 1)
        )
        last3_bear = all(
            float(df["close"].iloc[i]) < float(df["open"].iloc[i]) and
            (abs(float(df["close"].iloc[i]) - float(df["open"].iloc[i])) /
             max(float(df["high"].iloc[i]) - float(df["low"].iloc[i]), 0.0001)) > 0.6
            for i in range(idx - 2, idx + 1)
        )

        br = _body_ratio(idx)
        close = float(df["close"].iloc[idx])
        conf = Confidence.HIGH if br > 0.8 else Confidence.MEDIUM

        if last3_bull:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"3연속 강한 양봉 (quality_streak=strong_bull), "
                    f"body_ratio={br:.3f}"
                ),
                invalidation="body_ratio < 0.6 또는 음봉 발생",
                bull_case=f"body_ratio={br:.3f}, lower_wick={_lower_wick_ratio(idx):.3f}",
                bear_case=f"upper_wick={_upper_wick_ratio(idx):.3f}",
            )

        if last3_bear:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"3연속 강한 음봉 (quality_streak=strong_bear), "
                    f"body_ratio={br:.3f}"
                ),
                invalidation="body_ratio < 0.6 또는 양봉 발생",
                bull_case=f"lower_wick={_lower_wick_ratio(idx):.3f}",
                bear_case=f"body_ratio={br:.3f}, upper_wick={_upper_wick_ratio(idx):.3f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=f"quality_streak 조건 미충족. body_ratio={br:.3f}",
            invalidation="3연속 강한 양봉 또는 음봉 필요",
            bull_case=f"body_ratio={br:.3f}",
            bear_case=f"body_ratio={br:.3f}",
        )
