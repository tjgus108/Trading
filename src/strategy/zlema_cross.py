"""
ZLEMACrossStrategy: ZLEMA(9) vs ZLEMA(21) 크로스오버 전략.

ZLEMA(n): lag = (n-1)//2, adjusted = 2*close - close.shift(lag), ZLEMA = EMA(adjusted, n)
BUY  : ZLEMA9 상향 크로스 ZLEMA21
SELL : ZLEMA9 하향 크로스 ZLEMA21
HOLD : 그 외
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


def _zlema(series: pd.Series, period: int) -> pd.Series:
    lag = (period - 1) // 2
    adjusted = 2 * series - series.shift(lag)
    return adjusted.ewm(span=period, adjust=False).mean()


class ZLEMACrossStrategy(BaseStrategy):
    name = "zlema_cross"

    MIN_ROWS = 30
    FAST = 9
    SLOW = 21
    HIGH_CONF_THRESHOLD = 0.005  # 0.5% 이격

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
        zlema9 = _zlema(df["close"], self.FAST)
        zlema21 = _zlema(df["close"], self.SLOW)

        z9_now = float(zlema9.iloc[idx])
        z9_prev = float(zlema9.iloc[idx - 1])
        z21_now = float(zlema21.iloc[idx])
        z21_prev = float(zlema21.iloc[idx - 1])

        entry_price = float(df["close"].iloc[idx])

        cross_up = z9_prev <= z21_prev and z9_now > z21_now
        cross_down = z9_prev >= z21_prev and z9_now < z21_now

        separation = abs(z9_now - z21_now) / z21_now if z21_now != 0 else 0.0
        confidence = Confidence.HIGH if separation > self.HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"ZLEMA{self.FAST}({z9_now:.4f}) 이 ZLEMA{self.SLOW}({z21_now:.4f}) 상향 크로스 "
                    f"(이격 {separation*100:.3f}%)"
                ),
                invalidation=f"ZLEMA{self.FAST} 하향 크로스 시 청산",
                bull_case=f"ZLEMA 상향 크로스 — 단기 모멘텀 상승",
                bear_case="크로스가 fakeout일 수 있음",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"ZLEMA{self.FAST}({z9_now:.4f}) 이 ZLEMA{self.SLOW}({z21_now:.4f}) 하향 크로스 "
                    f"(이격 {separation*100:.3f}%)"
                ),
                invalidation=f"ZLEMA{self.FAST} 상향 크로스 시 청산",
                bull_case="크로스가 fakeout일 수 있음",
                bear_case=f"ZLEMA 하향 크로스 — 단기 모멘텀 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"ZLEMA 크로스 없음 — ZLEMA{self.FAST}={z9_now:.4f}, "
                f"ZLEMA{self.SLOW}={z21_now:.4f}"
            ),
            invalidation="크로스 발생 시 재평가",
        )
