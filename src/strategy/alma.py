"""
ALMA (Arnaud Legoux Moving Average) Cross 전략.
가우시안 가중 이동평균으로 노이즈를 최소화한 크로스오버 전략.

ALMA9 상향 크로스 ALMA21 → BUY
ALMA9 하향 크로스 ALMA21 → SELL
confidence: HIGH if 이격률 > 0.5%, MEDIUM otherwise
최소 30행 필요, idx = len(df) - 2
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

SIGMA = 6.0
OFFSET = 0.85
SHORT_PERIOD = 9
LONG_PERIOD = 21
DIVERGE_THRESH = 0.005  # 0.5%


def _alma(series: pd.Series, period: int, sigma: float = SIGMA, offset: float = OFFSET) -> pd.Series:
    m = int(offset * (period - 1))
    s = period / sigma
    weights = np.array([np.exp(-((i - m) ** 2) / (2 * s ** 2)) for i in range(period)])
    weights /= weights.sum()
    return series.rolling(period).apply(lambda x: (x * weights).sum(), raw=True)


class ALMAStrategy(BaseStrategy):
    name = "alma"

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 30
        if len(df) < min_rows:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="데이터 부족: 최소 30행 필요",
                invalidation="",
            )

        alma9 = _alma(df["close"], SHORT_PERIOD)
        alma21 = _alma(df["close"], LONG_PERIOD)

        idx = len(df) - 2
        entry = float(df["close"].iloc[idx])

        cur_a9 = float(alma9.iloc[idx])
        cur_a21 = float(alma21.iloc[idx])
        prev_a9 = float(alma9.iloc[idx - 1])
        prev_a21 = float(alma21.iloc[idx - 1])

        cross_up = (prev_a9 <= prev_a21) and (cur_a9 > cur_a21)
        cross_down = (prev_a9 >= prev_a21) and (cur_a9 < cur_a21)

        diverge = abs(cur_a9 - cur_a21) / max(cur_a21, 1e-10)
        confidence = Confidence.HIGH if diverge > DIVERGE_THRESH else Confidence.MEDIUM

        bull_case = (
            f"ALMA9={cur_a9:.4f} > ALMA21={cur_a21:.4f}, "
            f"이격률={diverge * 100:.3f}%"
        )
        bear_case = (
            f"ALMA9={cur_a9:.4f} < ALMA21={cur_a21:.4f}, "
            f"이격률={diverge * 100:.3f}%"
        )

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ALMA9 상향 크로스 ALMA21. "
                    f"ALMA9={cur_a9:.4f} > ALMA21={cur_a21:.4f}, "
                    f"이격률={diverge * 100:.3f}%"
                ),
                invalidation=f"ALMA9 < ALMA21 (하향 크로스)",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ALMA9 하향 크로스 ALMA21. "
                    f"ALMA9={cur_a9:.4f} < ALMA21={cur_a21:.4f}, "
                    f"이격률={diverge * 100:.3f}%"
                ),
                invalidation=f"ALMA9 > ALMA21 (상향 크로스)",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"크로스 없음. ALMA9={cur_a9:.4f}, ALMA21={cur_a21:.4f}, "
                f"이격률={diverge * 100:.3f}%"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
