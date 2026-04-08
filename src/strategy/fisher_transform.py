"""
FisherTransformStrategy: Fisher Transform 기반 추세 전환 전략.
"""

import numpy as np
import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class FisherTransformStrategy(BaseStrategy):
    name = "fisher_transform"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry_price = float(last["close"])

        if len(df) < 15:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry_price,
                reasoning="데이터 부족 (최소 15행 필요)",
                invalidation="데이터 충분 시 재평가",
            )

        idx = len(df) - 2
        period = 9

        high_max = df["high"].rolling(period).max()
        low_min = df["low"].rolling(period).min()
        x = 2 * (df["close"] - low_min) / (high_max - low_min + 1e-10) - 1
        x = x.clip(-0.999, 0.999)
        fisher = 0.5 * np.log((1 + x) / (1 - x))
        signal = fisher.shift(1)

        f_now = float(fisher.iloc[idx])
        f_prev = float(fisher.iloc[idx - 1])
        s_now = float(signal.iloc[idx])
        s_prev = float(signal.iloc[idx - 1])

        cross_up = f_prev <= s_prev and f_now > s_now and f_now > 0
        cross_down = f_prev >= s_prev and f_now < s_now and f_now < 0

        confidence = Confidence.HIGH if abs(f_now) > 2.0 else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"Fisher 상향 크로스: Fisher={f_now:.3f} > Signal={s_now:.3f}, Fisher>0",
                invalidation=f"Fisher < Signal 또는 Fisher < 0",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"Fisher 하향 크로스: Fisher={f_now:.3f} < Signal={s_now:.3f}, Fisher<0",
                invalidation=f"Fisher > Signal 또는 Fisher > 0",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=f"Fisher={f_now:.3f}, Signal={s_now:.3f} — 크로스 없음",
            invalidation="Fisher/Signal 크로스 발생 시 재평가",
        )
