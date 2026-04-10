"""
PriceActionScorerStrategy: 여러 가격 행동 지표를 합산한 점수 기반 진입 전략.
bull_score / bear_score >= 3 이면 진입, == 4 이면 HIGH confidence.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PriceActionScorerStrategy(BaseStrategy):
    name = "price_action_scorer"

    _MIN_ROWS = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Insufficient data",
                invalidation="",
            )

        open_ = df["open"]
        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        body = (close - open_).abs()
        total_range = (high - low + 1e-10)
        body_ratio = body / total_range

        upper_wick = high - close.combine(open_, max)
        lower_wick = close.combine(open_, min) - low

        vol_ma = volume.rolling(10, min_periods=1).mean()

        bull_score = (
            (close > open_).astype(int)
            + (body_ratio > 0.6).astype(int)
            + (lower_wick / total_range < 0.2).astype(int)
            + (volume > vol_ma).astype(int)
        )

        bear_score = (
            (close < open_).astype(int)
            + (body_ratio > 0.6).astype(int)
            + (upper_wick / total_range < 0.2).astype(int)
            + (volume > vol_ma).astype(int)
        )

        idx = len(df) - 2
        last = self._last(df)

        entry = float(last["close"])
        bs = int(bull_score.iloc[idx])
        ss = int(bear_score.iloc[idx])

        if pd.isna(entry) or pd.isna(bs) or pd.isna(ss):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN detected",
                invalidation="",
            )

        bull_case = (
            f"bull_score={bs}/4 | body_ratio={float(body_ratio.iloc[idx]):.2f} "
            f"lower_wick_ratio={float(lower_wick.iloc[idx] / total_range.iloc[idx]):.2f}"
        )
        bear_case = (
            f"bear_score={ss}/4 | body_ratio={float(body_ratio.iloc[idx]):.2f} "
            f"upper_wick_ratio={float(upper_wick.iloc[idx] / total_range.iloc[idx]):.2f}"
        )

        if bs >= 3:
            conf = Confidence.HIGH if bs == 4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"bull_score={bs}/4: strong bullish price action",
                invalidation=f"Close below low ({float(last['low']):.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if ss >= 3:
            conf = Confidence.HIGH if ss == 4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"bear_score={ss}/4: strong bearish price action",
                invalidation=f"Close above high ({float(last['high']):.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"bull_score={bs}, bear_score={ss}: no dominant signal",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
