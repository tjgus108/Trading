"""
NarrowRangeStrategy: NR7 감지 후 다음 봉 돌파 확인까지 포함한 전략.

- NR7: 최근 7봉(자신 포함) 중 현재봉의 range(high-low)가 가장 작음
- NR4: 최근 4봉(자신 포함) 중 최소 range
- Breakout BUY:  prev봉이 NR7 AND current close > prev high
- Breakout SELL: prev봉이 NR7 AND current close < prev low
- confidence: NR4 AND NR7 둘 다 충족 → HIGH, 아니면 MEDIUM
- 최소 행: 10

기존 nr7 전략과의 차이:
  - nr7: 단순 NR7 감지 (ATR 기반 confidence)
  - narrow_range: NR4/NR7 이중 조건 + 다음 봉 돌파 확인
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class NarrowRangeStrategy(BaseStrategy):
    name = "narrow_range"
    MIN_ROWS = 10

    def _is_nr(self, ranges: pd.Series, idx: int, n: int) -> bool:
        """idx번 봉이 최근 n봉 중 최소 range인지 확인."""
        if idx < n - 1:
            return False
        window = ranges.iloc[idx - n + 1: idx + 1]
        return float(ranges.iloc[idx]) <= float(window.min())

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        # current = 마지막 완성봉 (iloc[-2])
        # prev    = 그 이전 봉 (iloc[-3]) → NR7 후보
        curr_idx = len(df) - 2  # 완성봉
        prev_idx = curr_idx - 1  # NR7 후보봉

        if prev_idx < 6:
            return self._hold(df, "NR7 판단에 필요한 이전 봉 부족")

        ranges = df["high"] - df["low"]

        # prev봉이 NR7인지 확인 (직전 7봉 포함)
        is_nr7 = self._is_nr(ranges, prev_idx, 7)
        # prev봉이 NR4인지 확인
        is_nr4 = self._is_nr(ranges, prev_idx, 4)

        if not is_nr7:
            return self._hold(
                df,
                f"NR7 조건 미충족: prev_range={float(ranges.iloc[prev_idx]):.4f}",
            )

        close_curr = float(df["close"].iloc[curr_idx])
        high_prev = float(df["high"].iloc[prev_idx])
        low_prev = float(df["low"].iloc[prev_idx])
        prev_range = float(ranges.iloc[prev_idx])

        conf = Confidence.HIGH if (is_nr4 and is_nr7) else Confidence.MEDIUM

        bull_case = (
            f"NR7={'Y' if is_nr7 else 'N'} NR4={'Y' if is_nr4 else 'N'}, "
            f"close={close_curr:.4f} > prev_high={high_prev:.4f}, "
            f"prev_range={prev_range:.4f}"
        )
        bear_case = (
            f"NR7={'Y' if is_nr7 else 'N'} NR4={'Y' if is_nr4 else 'N'}, "
            f"close={close_curr:.4f} < prev_low={low_prev:.4f}, "
            f"prev_range={prev_range:.4f}"
        )

        # 상향 돌파
        if close_curr > high_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"NR7 후 상향 돌파: close({close_curr:.4f}) > prev_high({high_prev:.4f}), "
                    f"NR4={is_nr4}, conf={conf.value}"
                ),
                invalidation=f"close < prev_high({high_prev:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 하향 돌파
        if close_curr < low_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"NR7 후 하향 돌파: close({close_curr:.4f}) < prev_low({low_prev:.4f}), "
                    f"NR4={is_nr4}, conf={conf.value}"
                ),
                invalidation=f"close > prev_low({low_prev:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"NR7 감지됐으나 돌파 없음: close={close_curr:.4f} in [{low_prev:.4f}, {high_prev:.4f}]",
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
