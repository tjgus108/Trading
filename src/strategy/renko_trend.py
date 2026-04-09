"""
RenkoTrendStrategy: Renko 차트 시뮬레이션으로 추세 감지.
- Brick size = ATR14 EWM 평균
- 연속 상승 brick >= 3 → BUY, 연속 하락 brick >= 3 → SELL
- 5연속 이상 → HIGH confidence
"""

from typing import Optional, List

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class RenkoTrendStrategy(BaseStrategy):
    name = "renko_trend"

    MIN_ROWS = 20

    def _build_bricks(self, closes: np.ndarray, brick_size: float) -> List[int]:
        """
        Renko brick 방향 리스트 반환.
        +1: 상승 brick, -1: 하락 brick
        """
        if brick_size <= 0:
            return []

        bricks: List[int] = []
        last_close = closes[0]

        for close in closes[1:]:
            diff = close - last_close
            if diff >= brick_size:
                n = int(diff / brick_size)
                bricks.extend([1] * n)
                last_close += brick_size * n
            elif last_close - close >= brick_size:
                n = int((last_close - close) / brick_size)
                bricks.extend([-1] * n)
                last_close -= brick_size * n

        return bricks

    def _count_consecutive(self, bricks: List[int], direction: int) -> int:
        """끝에서부터 연속 brick 수 반환."""
        count = 0
        for b in reversed(bricks):
            if b == direction:
                count += 1
            else:
                break
        return count

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < self.MIN_ROWS:
            hold.reasoning = "데이터 부족"
            return hold

        last = self._last(df)
        entry = float(last["close"])
        hold.entry_price = entry

        closes = df["close"].values.astype(float)

        # ATR14 EWM으로 brick size 계산
        if "atr14" in df.columns:
            atr_series = df["atr14"]
        else:
            # ATR 직접 계산
            high = df["high"].values.astype(float)
            low = df["low"].values.astype(float)
            close = df["close"].values.astype(float)
            prev_close = np.roll(close, 1)
            prev_close[0] = close[0]
            tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
            atr_series = pd.Series(tr).ewm(span=14, adjust=False).mean()

        brick_size = float(atr_series.ewm(span=14, adjust=False).mean().iloc[-2])

        if brick_size <= 0:
            hold.reasoning = "brick_size <= 0"
            return hold

        bricks = self._build_bricks(closes[:-1], brick_size)  # -2까지 (마지막 완성봉 포함)

        if not bricks:
            hold.reasoning = "brick 생성 실패"
            return hold

        up_streak = self._count_consecutive(bricks, 1)
        down_streak = self._count_consecutive(bricks, -1)

        bull_case = f"연속 상승 brick={up_streak}, brick_size={brick_size:.4f}"
        bear_case = f"연속 하락 brick={down_streak}, brick_size={brick_size:.4f}"

        if up_streak >= 3:
            confidence = Confidence.HIGH if up_streak >= 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Renko 연속 상승 {up_streak}개. brick_size={brick_size:.4f}",
                invalidation=f"하락 brick 발생 시",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if down_streak >= 3:
            confidence = Confidence.HIGH if down_streak >= 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Renko 연속 하락 {down_streak}개. brick_size={brick_size:.4f}",
                invalidation=f"상승 brick 발생 시",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = f"연속 brick 부족 (up={up_streak}, down={down_streak})"
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold
