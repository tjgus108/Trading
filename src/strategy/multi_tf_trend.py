"""
MultiTFTrendStrategy: 단일 데이터에서 여러 시간대 추세를 합성하여 신호 생성.

지표:
  - 단기(fast): EMA10 vs EMA20
  - 중기(mid): EMA20 vs EMA50
  - 장기(slow): EMA50 vs EMA100
  - score = 상승 시간대 수 (0~3)

신호:
  - BUY: score == 3 (모든 시간대 상승 정렬)
  - SELL: score == 0 (모든 시간대 하락 정렬)
  - HOLD: score 1 또는 2 (혼합)
- confidence: HIGH if score==3 AND prev_score<3 (새로운 정렬) else MEDIUM
- 최소 행: 110
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 110


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


class MultiTFTrendStrategy(BaseStrategy):
    name = "multi_tf_trend"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for multi_tf_trend")

        close = df["close"].astype(float)

        ema10 = _ema(close, 10)
        ema20 = _ema(close, 20)
        ema50 = _ema(close, 50)
        ema100 = _ema(close, 100)

        idx = len(df) - 2  # 마지막 완성봉
        prev_idx = idx - 1

        import math

        def get_score(i: int) -> Optional[int]:
            vals = [ema10.iloc[i], ema20.iloc[i], ema50.iloc[i], ema100.iloc[i]]
            if any(math.isnan(v) for v in vals):
                return None
            up_fast = vals[0] > vals[1]
            up_mid = vals[1] > vals[2]
            up_slow = vals[2] > vals[3]
            return int(up_fast) + int(up_mid) + int(up_slow)

        score = get_score(idx)
        prev_score = get_score(prev_idx)

        if score is None or prev_score is None:
            return self._hold(df, "Insufficient data for multi_tf_trend")

        entry = float(close.iloc[idx])

        if score == 3:
            is_new_alignment = prev_score < 3
            conf = Confidence.HIGH if is_new_alignment else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Multi-TF trend score={score}: all timeframes bullish aligned",
                invalidation=f"Score drops below 3 (any EMA cross bearish)",
                bull_case="All fast/mid/slow EMAs bullish aligned",
                bear_case="Any EMA cross would break alignment",
            )

        if score == 0:
            is_new_alignment = prev_score > 0
            conf = Confidence.HIGH if is_new_alignment else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Multi-TF trend score={score}: all timeframes bearish aligned",
                invalidation=f"Score rises above 0 (any EMA cross bullish)",
                bull_case="Any EMA cross would break bearish alignment",
                bear_case="All fast/mid/slow EMAs bearish aligned",
            )

        return self._hold(df, f"Multi-TF trend score={score}: mixed timeframe signals")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is not None and len(df) >= 2:
            entry = float(df["close"].iloc[-2])
        else:
            entry = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
