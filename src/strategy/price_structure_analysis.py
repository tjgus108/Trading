"""
PriceStructureAnalysisStrategy:
- BUY:  higher_high AND higher_low  (상승 구조)
- SELL: lower_low AND lower_high    (하락 구조)
- confidence: HIGH if close > recent_high.shift(1) (BUY) or close < recent_low.shift(1) (SELL) else MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class PriceStructureAnalysisStrategy(BaseStrategy):
    name = "price_structure_analysis"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족")

        high = df["high"]
        low = df["low"]
        close = df["close"]

        # 로컬 고점/저점 (lookahead 없음: shift(3) 적용)
        local_high = high.rolling(5, min_periods=1).max().shift(3)
        local_low = low.rolling(5, min_periods=1).min().shift(3)

        # 최근 고점/저점
        recent_high = high.rolling(10, min_periods=1).max()
        recent_low = low.rolling(10, min_periods=1).min()

        # 구조 판단
        higher_high = recent_high > recent_high.shift(5)
        higher_low = recent_low > recent_low.shift(5)
        lower_low = recent_low < recent_low.shift(5)
        lower_high = recent_high < recent_high.shift(5)

        idx = len(df) - 2

        # NaN 체크
        needed = [
            recent_high.iloc[idx], recent_low.iloc[idx],
            recent_high.shift(1).iloc[idx], recent_low.shift(1).iloc[idx],
            higher_high.iloc[idx], higher_low.iloc[idx],
            lower_low.iloc[idx], lower_high.iloc[idx],
        ]
        if any(pd.isna(v) for v in needed):
            return self._hold(df, "NaN 데이터")

        last_close = float(close.iloc[idx])
        last_higher_high = bool(higher_high.iloc[idx])
        last_higher_low = bool(higher_low.iloc[idx])
        last_lower_low = bool(lower_low.iloc[idx])
        last_lower_high = bool(lower_high.iloc[idx])
        last_recent_high = float(recent_high.iloc[idx])
        last_recent_low = float(recent_low.iloc[idx])
        prev_recent_high = float(recent_high.shift(1).iloc[idx])
        prev_recent_low = float(recent_low.shift(1).iloc[idx])

        info = (
            f"close={last_close:.4f} recent_high={last_recent_high:.4f} "
            f"recent_low={last_recent_low:.4f} "
            f"HH={last_higher_high} HL={last_higher_low} "
            f"LL={last_lower_low} LH={last_lower_high}"
        )

        if last_higher_high and last_higher_low:
            confidence = Confidence.HIGH if last_close > prev_recent_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"상승 구조 (HH+HL): {info}",
                invalidation=f"recent_low 하락 반전",
                bull_case=info,
                bear_case=info,
            )

        if last_lower_low and last_lower_high:
            confidence = Confidence.HIGH if last_close < prev_recent_low else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"하락 구조 (LL+LH): {info}",
                invalidation=f"recent_high 상승 반전",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"구조 불명확: {info}")

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
