"""
DualEMACrossStrategy: EMA3개(5/13/34 피보나치) 완전 정렬 + 크로스 확인.

BUY : EMA5 > EMA13 > EMA34 AND EMA5가 EMA13 상향 크로스 (prev5<=prev13, now5>now13)
SELL: EMA5 < EMA13 < EMA34 AND EMA5가 EMA13 하향 크로스
Confidence HIGH: (EMA5 - EMA34) / close > 1.5%
최소 행: 40
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class DualEMACrossStrategy(BaseStrategy):
    name = "dual_ema_cross"

    MIN_ROWS = 40
    FAST = 5
    MID = 13
    SLOW = 34
    HIGH_CONF_THRESHOLD = 0.015  # 1.5%

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"데이터 부족 (최소 {self.MIN_ROWS}행 필요)",
                invalidation="N/A",
            )

        ema5 = df["close"].ewm(span=self.FAST, adjust=False).mean()
        ema13 = df["close"].ewm(span=self.MID, adjust=False).mean()
        ema34 = df["close"].ewm(span=self.SLOW, adjust=False).mean()

        idx = len(df) - 2  # 마지막 완성봉

        e5_now = float(ema5.iloc[idx])
        e13_now = float(ema13.iloc[idx])
        e34_now = float(ema34.iloc[idx])
        e5_prev = float(ema5.iloc[idx - 1])
        e13_prev = float(ema13.iloc[idx - 1])

        entry_price = float(df["close"].iloc[idx])

        # 완전 정렬 확인
        bull_aligned = e5_now > e13_now > e34_now
        bear_aligned = e5_now < e13_now < e34_now

        # EMA5/EMA13 크로스 확인
        cross_up = e5_prev <= e13_prev and e5_now > e13_now
        cross_down = e5_prev >= e13_prev and e5_now < e13_now

        # Confidence 계산
        spread = abs(e5_now - e34_now) / entry_price if entry_price != 0 else 0.0
        confidence = Confidence.HIGH if spread > self.HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if bull_aligned and cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EMA{self.FAST}({e5_now:.4f}) > EMA{self.MID}({e13_now:.4f}) > EMA{self.SLOW}({e34_now:.4f}) "
                    f"완전 상승 정렬, EMA{self.FAST} 상향 크로스 확인. 이격={spread*100:.2f}%"
                ),
                invalidation=f"EMA{self.FAST} 하향 크로스 또는 정렬 붕괴",
                bull_case=f"피보나치 EMA 3중 정렬 상승. 이격 {spread*100:.2f}%",
                bear_case="크로스가 fakeout일 수 있음",
            )

        if bear_aligned and cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EMA{self.FAST}({e5_now:.4f}) < EMA{self.MID}({e13_now:.4f}) < EMA{self.SLOW}({e34_now:.4f}) "
                    f"완전 하락 정렬, EMA{self.FAST} 하향 크로스 확인. 이격={spread*100:.2f}%"
                ),
                invalidation=f"EMA{self.FAST} 상향 크로스 또는 정렬 붕괴",
                bull_case="크로스가 fakeout일 수 있음",
                bear_case=f"피보나치 EMA 3중 정렬 하락. 이격 {spread*100:.2f}%",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"조건 미충족 — EMA{self.FAST}={e5_now:.4f}, "
                f"EMA{self.MID}={e13_now:.4f}, EMA{self.SLOW}={e34_now:.4f}"
            ),
            invalidation="크로스 + 완전 정렬 시 재평가",
        )
