"""
PriceCompressionSignalStrategy: NR7 가격 압축 + 방향 돌파 전략.

- NR7: 최근 7봉 중 가장 좁은 range (가격 압축 신호)
- BUY:  nr7 AND close > prev 3봉 고가 최대값
- SELL: nr7 AND close < prev 3봉 저가 최소값
- confidence: daily_range < 20봉 평균 range * 0.5 → HIGH, 그 외 MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PriceCompressionSignalStrategy(BaseStrategy):
    name = "price_compression_signal"
    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        high = df["high"]
        low = df["low"]
        close = df["close"]

        daily_range = high - low
        nr7 = daily_range == daily_range.rolling(7, min_periods=1).min()
        prev_high = high.rolling(3, min_periods=1).max().shift(1)
        prev_low = low.rolling(3, min_periods=1).min().shift(1)

        idx = len(df) - 2
        row = df.iloc[idx]

        c = float(close.iloc[idx])
        dr = float(daily_range.iloc[idx])
        is_nr7 = bool(nr7.iloc[idx])
        ph = float(prev_high.iloc[idx]) if not pd.isna(prev_high.iloc[idx]) else None
        pl = float(prev_low.iloc[idx]) if not pd.isna(prev_low.iloc[idx]) else None
        avg_range = float(daily_range.rolling(20, min_periods=1).mean().iloc[idx])

        # NaN 체크
        if ph is None or pl is None or pd.isna(avg_range) or pd.isna(dr):
            return self._hold(df, "NaN 값 감지")

        if not is_nr7:
            return self._hold(
                df,
                f"NR7 조건 미충족: range={dr:.4f}, min7={float(daily_range.rolling(7, min_periods=1).min().iloc[idx]):.4f}",
            )

        conf = Confidence.HIGH if dr < avg_range * 0.5 else Confidence.MEDIUM

        bull_case = (
            f"NR7=True, close={c:.4f} > prev_high={ph:.4f}, "
            f"range={dr:.4f}, avg_range={avg_range:.4f}, conf={conf.value}"
        )
        bear_case = (
            f"NR7=True, close={c:.4f} < prev_low={pl:.4f}, "
            f"range={dr:.4f}, avg_range={avg_range:.4f}, conf={conf.value}"
        )

        # BUY: 압축 후 상향 돌파
        if c > ph:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"NR7 압축 후 상향 돌파: close({c:.4f}) > prev_high({ph:.4f}), "
                    f"range={dr:.4f}, conf={conf.value}"
                ),
                invalidation=f"close < prev_high({ph:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 압축 후 하향 돌파
        if c < pl:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"NR7 압축 후 하향 돌파: close({c:.4f}) < prev_low({pl:.4f}), "
                    f"range={dr:.4f}, conf={conf.value}"
                ),
                invalidation=f"close > prev_low({pl:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"NR7 감지됐으나 돌파 없음: close={c:.4f} in [{pl:.4f}, {ph:.4f}]",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
