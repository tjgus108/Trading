"""
CandleBodyFilter 전략:
- 최근 3봉 중 강한 방향성 봉(body_ratio > 0.6) 카운팅
- BUY:  bull_streak >= 2 AND close > close.shift(1) AND volume > vol_ma
- SELL: bear_streak >= 2 AND close < close.shift(1) AND volume > vol_ma
- confidence: HIGH if streak == 3, MEDIUM otherwise
- 최소 데이터: 20행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class CandleBodyFilterStrategy(BaseStrategy):
    name = "candle_body_filter"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        open_ = df["open"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        body = (close - open_).abs()
        total_range = (high - low + 1e-10)
        body_ratio = body / total_range

        strong_bull = (close > open_) & (body_ratio > 0.6)
        strong_bear = (close < open_) & (body_ratio > 0.6)

        bull_streak = strong_bull.rolling(3, min_periods=1).sum()
        bear_streak = strong_bear.rolling(3, min_periods=1).sum()

        vol_ma = volume.rolling(10, min_periods=1).mean()

        idx = len(df) - 2
        last = df.iloc[idx]

        bull_s = bull_streak.iloc[idx]
        bear_s = bear_streak.iloc[idx]
        c = float(close.iloc[idx])
        c_prev = float(close.iloc[idx - 1]) if idx >= 1 else c
        vol = float(volume.iloc[idx])
        vma = float(vol_ma.iloc[idx])

        if pd.isna(bull_s) or pd.isna(bear_s) or pd.isna(vma):
            return self._hold(df, "NaN in indicators")

        context = (
            f"close={c:.2f} bull_streak={bull_s:.0f} bear_streak={bear_s:.0f} "
            f"vol={vol:.0f} vol_ma={vma:.0f}"
        )

        # BUY
        if bull_s >= 2 and c > c_prev and vol > vma:
            confidence = Confidence.HIGH if bull_s == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"CandleBodyFilter BUY: bull_streak={bull_s:.0f}, vol 확인",
                invalidation="음봉 발생 또는 volume 감소",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if bear_s >= 2 and c < c_prev and vol > vma:
            confidence = Confidence.HIGH if bear_s == 3 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"CandleBodyFilter SELL: bear_streak={bear_s:.0f}, vol 확인",
                invalidation="양봉 발생 또는 volume 감소",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
