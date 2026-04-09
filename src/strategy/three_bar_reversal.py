"""
ThreeBarReversalStrategy: 3봉 반전 패턴 전략.
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class ThreeBarReversalStrategy(BaseStrategy):
    name = "three_bar_reversal"

    MIN_ROWS = 15

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족 (최소 {self.MIN_ROWS}행 필요)",
                invalidation="N/A",
            )

        # current = idx-1 기준 (마지막 완성봉)
        idx = len(df) - 2   # current
        prev1_idx = idx - 1  # prev1 (inside bar)
        prev2_idx = idx - 2  # prev2 (첫 번째봉)

        open2 = float(df["open"].iloc[prev2_idx])
        close2 = float(df["close"].iloc[prev2_idx])
        high2 = float(df["high"].iloc[prev2_idx])
        low2 = float(df["low"].iloc[prev2_idx])

        high1 = float(df["high"].iloc[prev1_idx])
        low1 = float(df["low"].iloc[prev1_idx])

        open_curr = float(df["open"].iloc[idx])
        close_curr = float(df["close"].iloc[idx])
        high_curr = float(df["high"].iloc[idx])
        low_curr = float(df["low"].iloc[idx])

        # Inside bar: prev1 완전히 prev2 내부
        is_inside = high1 < high2 and low1 > low2

        # 볼륨
        vol_curr = float(df["volume"].iloc[idx])
        avg_vol_10 = float(df["volume"].iloc[max(0, idx - 10):idx].mean())
        vol_confirm = avg_vol_10 > 0 and vol_curr > avg_vol_10 * 1.2

        # prev2 봉 방향
        is_prev2_bearish = close2 < open2
        is_prev2_bullish = close2 > open2

        # current 봉 방향
        is_curr_bullish = close_curr > open_curr
        is_curr_bearish = close_curr < open_curr

        # Bullish 3-bar reversal
        is_bullish = (
            is_prev2_bearish
            and is_inside
            and is_curr_bullish
            and close_curr > open2
        )

        # Bearish 3-bar reversal
        is_bearish = (
            is_prev2_bullish
            and is_inside
            and is_curr_bearish
            and close_curr < open2
        )

        # Confidence: current candle range > 2x prev1 range → HIGH
        range_curr = high_curr - low_curr
        range_prev1 = high1 - low1
        strong = range_prev1 > 0 and range_curr > range_prev1 * 2
        confidence = Confidence.HIGH if strong else Confidence.MEDIUM

        if is_bullish and vol_confirm:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish 3-Bar Reversal. "
                    f"prev2 음봉(O={open2:.4f},C={close2:.4f}), "
                    f"prev1 inside bar(H={high1:.4f},L={low1:.4f}), "
                    f"current 양봉(C={close_curr:.4f}) > prev2 open({open2:.4f}). "
                    f"volume={vol_curr:.0f} > avg*1.2({avg_vol_10 * 1.2:.0f})"
                ),
                invalidation=f"close {close_curr:.4f} 하회 시 무효",
                bull_case="3봉 반전 패턴 + 거래량 확인",
                bear_case="모멘텀 약화 시 추가 하락 가능",
            )

        if is_bearish and vol_confirm:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish 3-Bar Reversal. "
                    f"prev2 양봉(O={open2:.4f},C={close2:.4f}), "
                    f"prev1 inside bar(H={high1:.4f},L={low1:.4f}), "
                    f"current 음봉(C={close_curr:.4f}) < prev2 open({open2:.4f}). "
                    f"volume={vol_curr:.0f} > avg*1.2({avg_vol_10 * 1.2:.0f})"
                ),
                invalidation=f"close {close_curr:.4f} 상회 시 무효",
                bull_case="저항 존 돌파 시 추가 상승 가능",
                bear_case="3봉 반전 패턴 + 거래량 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="3-Bar Reversal 패턴 미감지 (HOLD)",
            invalidation="N/A",
        )
