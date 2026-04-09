"""
PsychologicalLineStrategy: 최근 N봉 중 상승 봉 비율(Psychological Line) 기반 전략.
PL < 25 & 현재 봉 상승 → BUY, PL > 75 & 현재 봉 하락 → SELL.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PsychologicalLineStrategy(BaseStrategy):
    name = "psychological_line"

    def __init__(self, period: int = 12, buy_threshold: float = 25.0, sell_threshold: float = 75.0,
                 high_buy: float = 17.0, high_sell: float = 83.0):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.high_buy = high_buy
        self.high_sell = high_sell

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 15
        if len(df) < min_rows:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="PL 계산에 필요한 데이터 부족 (최소 15행).",
                invalidation="",
            )

        period = self.period
        up_days = (df["close"].diff() > 0).rolling(period).sum()
        pl = up_days / period * 100

        idx = len(df) - 2
        pl_now = float(pl.iloc[idx])
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])
        rising = close_now > close_prev
        falling = close_now < close_prev
        entry = close_now

        reasoning_base = (
            f"PL={pl_now:.1f}%, close={close_now:.4f}, prev_close={close_prev:.4f}"
        )

        if pl_now < self.buy_threshold and rising:
            confidence = Confidence.HIGH if pl_now < self.high_buy else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PL {pl_now:.1f}% (극단적 비관) & 현재 봉 상승. {reasoning_base}",
                invalidation="PL 반등 실패 또는 현재 봉 하락 전환 시 무효.",
                bull_case="극단적 비관 구간에서 반등 신호 포착.",
                bear_case="추가 하락으로 PL 더 낮아질 위험.",
            )

        if pl_now > self.sell_threshold and falling:
            confidence = Confidence.HIGH if pl_now > self.high_sell else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PL {pl_now:.1f}% (극단적 낙관) & 현재 봉 하락. {reasoning_base}",
                invalidation="PL 하락 실패 또는 현재 봉 상승 전환 시 무효.",
                bull_case="PL 하락 미실현 시 추가 상승 가능.",
                bear_case="극단적 낙관 구간에서 하락 반전 시작.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"PL 임계값 미달 또는 봉 방향 조건 불충족. {reasoning_base}",
            invalidation=f"PL < {self.buy_threshold} & 상승봉 또는 PL > {self.sell_threshold} & 하락봉 시 신호.",
        )
