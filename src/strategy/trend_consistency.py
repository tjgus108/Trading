"""
TrendConsistency 전략: 다중 EMA 일관성 점수 기반 추세 추종.
bull_count(0~3): close>ema5, ema5>ema10, ema10>ema20 개수
bear_count(0~3): close<ema5, ema5<ema10, ema10<ema20 개수
BUY: bull_count==3 AND close > prev_close
SELL: bear_count==3 AND close < prev_close
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendConsistencyStrategy(BaseStrategy):
    name = "trend_consistency"

    _MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"Not enough data: {len(df)} < {self._MIN_ROWS}",
                invalidation="",
            )

        close = df["close"]
        idx = len(df) - 2

        ema5 = close.ewm(span=5, adjust=False).mean()
        ema10 = close.ewm(span=10, adjust=False).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()

        bull_count = (
            (close > ema5).astype(int)
            + (ema5 > ema10).astype(int)
            + (ema10 > ema20).astype(int)
        )
        bear_count = (
            (close < ema5).astype(int)
            + (ema5 < ema10).astype(int)
            + (ema10 < ema20).astype(int)
        )

        last = self._last(df)
        entry = float(last["close"])
        prev_close = float(close.iloc[idx - 1]) if idx >= 1 else entry

        bull_val = int(bull_count.iloc[idx])
        bear_val = int(bear_count.iloc[idx])

        ema5_val = float(ema5.iloc[idx])
        ema10_val = float(ema10.iloc[idx])
        ema20_val = float(ema20.iloc[idx])

        # NaN 체크
        if any(
            pd.isna(v) for v in [entry, prev_close, ema5_val, ema10_val, ema20_val]
        ):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in indicators",
                invalidation="",
            )

        bull_case = (
            f"bull_count={bull_val}, EMA5={ema5_val:.4f}, "
            f"EMA10={ema10_val:.4f}, EMA20={ema20_val:.4f}"
        )
        bear_case = (
            f"bear_count={bear_val}, EMA5={ema5_val:.4f}, "
            f"EMA10={ema10_val:.4f}, EMA20={ema20_val:.4f}"
        )

        if bull_val >= 3 and entry > prev_close:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if bull_val == 3 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Full bullish EMA stack (bull_count=3). "
                    f"Close {entry:.4f} > prev {prev_close:.4f}."
                ),
                invalidation=f"Close below EMA5 ({ema5_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bear_val >= 3 and entry < prev_close:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if bear_val == 3 else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Full bearish EMA stack (bear_count=3). "
                    f"Close {entry:.4f} < prev {prev_close:.4f}."
                ),
                invalidation=f"Close above EMA5 ({ema5_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No full EMA alignment. bull_count={bull_val}, bear_count={bear_val}."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
