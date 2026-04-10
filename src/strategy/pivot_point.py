"""
PivotPointStrategy: 이전 봉 기반 피벗 포인트 돌파 전략.
- BUY:  close > pivot AND close > r1
- SELL: close < pivot AND close < s1
- HIGH confidence: close > r2 (BUY) or close < s2 (SELL)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class PivotPointStrategy(BaseStrategy):
    name = "pivot_point"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족 (최소 20행 필요)")

        idx = len(df) - 2
        close = df["close"]
        high = df["high"]
        low = df["low"]

        prev_high = float(high.shift(1).iloc[idx])
        prev_low = float(low.shift(1).iloc[idx])
        prev_close = float(close.shift(1).iloc[idx])
        cur_close = float(close.iloc[idx])

        # NaN 체크
        if any(v != v for v in [prev_high, prev_low, prev_close, cur_close]):
            return self._hold(df, "NaN 값 감지")

        pivot = (prev_high + prev_low + prev_close) / 3
        r1 = 2 * pivot - prev_low   # resistance 1
        s1 = 2 * pivot - prev_high  # support 1
        r2 = pivot + (prev_high - prev_low)  # resistance 2
        s2 = pivot - (prev_high - prev_low)  # support 2

        context = (
            f"close={cur_close:.4f} pivot={pivot:.4f} "
            f"R1={r1:.4f} R2={r2:.4f} S1={s1:.4f} S2={s2:.4f}"
        )

        # BUY: 피벗 돌파 + R1 돌파
        if cur_close > pivot and cur_close > r1:
            conf = Confidence.HIGH if cur_close > r2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=cur_close,
                reasoning=f"피벗 돌파 + R1 돌파: {context}",
                invalidation=f"close < R1({r1:.4f}) 하향 이탈 시",
                bull_case=f"R2={r2:.4f} 돌파 시 추가 상승 기대",
                bear_case=f"R1={r1:.4f} 저항 반락 가능",
            )

        # SELL: 피벗 하향 + S1 이탈
        if cur_close < pivot and cur_close < s1:
            conf = Confidence.HIGH if cur_close < s2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=cur_close,
                reasoning=f"피벗 하향 + S1 이탈: {context}",
                invalidation=f"close > S1({s1:.4f}) 회복 시",
                bull_case=f"S2={s2:.4f} 지지 반등 가능",
                bear_case=f"S2={s2:.4f} 하향 이탈 시 추가 하락",
            )

        return self._hold(df, f"피벗 신호 없음: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
