"""
Opening Range Breakout 전략:
처음 N봉(기본 5)을 오프닝 레인지로 설정하고,
close가 range_high를 상방 돌파하면 BUY,
close가 range_low를 하방 돌파하면 SELL.
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class OpeningRangeBreakoutStrategy(BaseStrategy):
    name = "opening_range_breakout"

    def __init__(self, range_bars: int = 5) -> None:
        self.range_bars = range_bars

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = self.range_bars + 5
        if len(df) < min_rows:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"데이터 부족: {len(df)} < {min_rows}",
                invalidation="",
            )

        opening = df.iloc[: self.range_bars]
        range_high: float = float(opening["high"].max())
        range_low: float = float(opening["low"].min())
        range_size: float = range_high - range_low

        last = self._last(df)
        close: float = float(last["close"])
        entry: float = close

        threshold: float = range_size * 0.01

        bull_case = (
            f"close({close:.4f}) > range_high({range_high:.4f}), "
            f"range={range_size:.4f}, threshold={threshold:.4f}"
        )
        bear_case = (
            f"close({close:.4f}) < range_low({range_low:.4f}), "
            f"range={range_size:.4f}, threshold={threshold:.4f}"
        )

        if close > range_high:
            breakout: float = close - range_high
            conf = Confidence.HIGH if breakout > threshold else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"상방 돌파: close({close:.4f}) > range_high({range_high:.4f}), "
                    f"breakout={breakout:.4f}, threshold={threshold:.4f}"
                ),
                invalidation=f"close가 range_high({range_high:.4f}) 아래로 복귀",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if close < range_low:
            breakout = range_low - close
            conf = Confidence.HIGH if breakout > threshold else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"하방 돌파: close({close:.4f}) < range_low({range_low:.4f}), "
                    f"breakout={breakout:.4f}, threshold={threshold:.4f}"
                ),
                invalidation=f"close가 range_low({range_low:.4f}) 위로 복귀",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"레인지 내 유지: close({close:.4f}) in "
                f"[{range_low:.4f}, {range_high:.4f}]"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
