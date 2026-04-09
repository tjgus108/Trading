"""
Range Expansion 전략:
- True Range (TR) = max(high-low, |high-prev_close|, |low-prev_close|)
- avg_tr_20 = TR.rolling(20).mean()
- BUY:  TR > avg_tr_20 * 1.5 AND close > open (양봉 + 범위 확장)
- SELL: TR > avg_tr_20 * 1.5 AND close < open (음봉 + 범위 확장)
- confidence: HIGH if TR > avg_tr_20 * 2.0, MEDIUM if > 1.5
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
TR_THRESHOLD_MED = 1.5
TR_THRESHOLD_HIGH = 2.0


def _compute_tr(df: pd.DataFrame) -> pd.Series:
    """True Range 계산."""
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr


class RangeExpansionStrategy(BaseStrategy):
    name = "range_expansion"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning=f"데이터 부족: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        tr = _compute_tr(df)
        avg_tr_20 = tr.rolling(20).mean()

        last = self._last(df)  # df.iloc[-2]
        last_idx = len(df) - 2

        tr_val = float(tr.iloc[last_idx])
        avg_val = float(avg_tr_20.iloc[last_idx])

        if avg_val == 0 or np.isnan(avg_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="avg_tr_20 계산 불가 (NaN 또는 0)",
                invalidation="",
            )

        ratio = tr_val / avg_val
        close = float(last["close"])
        open_ = float(last["open"])
        is_bull = close > open_
        is_bear = close < open_

        expanded = ratio > TR_THRESHOLD_MED
        conf = Confidence.HIGH if ratio > TR_THRESHOLD_HIGH else Confidence.MEDIUM

        reasoning_base = (
            f"TR={tr_val:.4f}, avg_tr_20={avg_val:.4f}, ratio={ratio:.2f}"
        )

        if expanded and is_bull:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"양봉 + 범위 확장. {reasoning_base}",
                invalidation=f"Close below open {open_:.4f}",
                bull_case=f"TR/avg={ratio:.2f}x 범위 확장 양봉",
                bear_case="범위 확장 없거나 음봉",
            )

        if expanded and is_bear:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"음봉 + 범위 확장. {reasoning_base}",
                invalidation=f"Close above open {open_:.4f}",
                bull_case="범위 확장 없거나 양봉",
                bear_case=f"TR/avg={ratio:.2f}x 범위 확장 음봉",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"범위 확장 미충족 또는 도지. {reasoning_base}",
            invalidation="",
            bull_case="TR 확장 + 양봉 필요",
            bear_case="TR 확장 + 음봉 필요",
        )
