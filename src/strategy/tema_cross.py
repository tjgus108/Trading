"""
TEMACrossStrategy: TEMA(8) vs TEMA(21) 크로스오버 전략.

TEMA(n) = 3*EMA1 - 3*EMA2 + EMA3
BUY  : TEMA8 상향 크로스
SELL : TEMA8 하향 크로스
HOLD : 그 외
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


def _tema(series: pd.Series, period: int) -> pd.Series:
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    return 3 * ema1 - 3 * ema2 + ema3


class TEMACrossStrategy(BaseStrategy):
    name = "tema_cross"

    MIN_ROWS = 30
    FAST = 8
    SLOW = 21
    HIGH_CONF_THRESHOLD = 0.008  # 0.8% 이격

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 30행 필요)",
                invalidation="N/A",
            )

        idx = len(df) - 2
        tema8 = _tema(df["close"], self.FAST)
        tema21 = _tema(df["close"], self.SLOW)

        t8_now = float(tema8.iloc[idx])
        t8_prev = float(tema8.iloc[idx - 1])
        t21_now = float(tema21.iloc[idx])
        t21_prev = float(tema21.iloc[idx - 1])

        entry_price = float(df["close"].iloc[idx])

        cross_up = t8_prev <= t21_prev and t8_now > t21_now
        cross_down = t8_prev >= t21_prev and t8_now < t21_now

        separation = abs(t8_now - t21_now) / t21_now if t21_now != 0 else 0.0
        confidence = Confidence.HIGH if separation > self.HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"TEMA{self.FAST}({t8_now:.4f}) 이 TEMA{self.SLOW}({t21_now:.4f}) 상향 크로스 "
                    f"(이격 {separation*100:.3f}%)"
                ),
                invalidation=f"TEMA{self.FAST} 하향 크로스 시 청산",
                bull_case=f"TEMA 상향 크로스 — 단기 모멘텀 상승",
                bear_case="크로스가 fakeout일 수 있음",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"TEMA{self.FAST}({t8_now:.4f}) 이 TEMA{self.SLOW}({t21_now:.4f}) 하향 크로스 "
                    f"(이격 {separation*100:.3f}%)"
                ),
                invalidation=f"TEMA{self.FAST} 상향 크로스 시 청산",
                bull_case="크로스가 fakeout일 수 있음",
                bear_case=f"TEMA 하향 크로스 — 단기 모멘텀 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"TEMA 크로스 없음 — TEMA{self.FAST}={t8_now:.4f}, "
                f"TEMA{self.SLOW}={t21_now:.4f}"
            ),
            invalidation="크로스 발생 시 재평가",
        )
