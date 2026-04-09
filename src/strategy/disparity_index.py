"""
DisparityIndexStrategy: 종가와 EMA20의 괴리율(Disparity Index) 기반 전략.
DI < -5 & 반등 → BUY, DI > 5 & 반락 → SELL.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class DisparityIndexStrategy(BaseStrategy):
    name = "disparity_index"

    def __init__(self, ema_span: int = 20, threshold: float = 5.0, high_threshold: float = 8.0):
        self.ema_span = ema_span
        self.threshold = threshold
        self.high_threshold = high_threshold

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 25
        if len(df) < min_rows:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="DI 계산에 필요한 데이터 부족 (최소 25행).",
                invalidation="",
            )

        ema20 = df["close"].ewm(span=self.ema_span, adjust=False).mean()
        di = (df["close"] - ema20) / ema20 * 100

        idx = len(df) - 2
        di_now = float(di.iloc[idx])
        di_prev = float(di.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        reasoning_base = (
            f"DI={di_now:.2f}, DI_prev={di_prev:.2f}, close={entry:.4f}"
        )

        if di_now < -self.threshold and di_now > di_prev:
            confidence = Confidence.HIGH if abs(di_now) > self.high_threshold else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DI {di_now:.2f} (EMA 대비 {abs(di_now):.1f}% 이탈 후 반등). {reasoning_base}",
                invalidation="DI가 다시 하락 전환 시 무효.",
                bull_case="EMA 대비 과도한 낙폭 후 반등 시작.",
                bear_case="추가 하락으로 DI 재차 감소 위험.",
            )

        if di_now > self.threshold and di_now < di_prev:
            confidence = Confidence.HIGH if abs(di_now) > self.high_threshold else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DI {di_now:.2f} (EMA 대비 {abs(di_now):.1f}% 과열 후 반락). {reasoning_base}",
                invalidation="DI가 다시 상승 전환 시 무효.",
                bull_case="DI 반락 후 EMA 수렴 실패 시 추가 상승 가능.",
                bear_case="EMA 대비 과도한 상승 후 하락 반전.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"DI 임계값 미달 또는 방향 조건 불충족. {reasoning_base}",
            invalidation=f"|DI| > {self.threshold} 및 방향 전환 시 신호 발생.",
        )
