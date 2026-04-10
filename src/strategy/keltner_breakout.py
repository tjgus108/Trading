"""
KeltnerBreakoutStrategy: 순수 Keltner Channel 돌파 전략.

로직:
  - EMA20 + 2*ATR14 = kc_upper
  - EMA20 - 2*ATR14 = kc_lower
  - ATR: max(high-low, |high-prev_close|, |low-prev_close|), 14기간 rolling mean
  - BUY:  이전봉 close < kc_upper AND 현재봉 close > kc_upper (상단 돌파)
  - SELL: 이전봉 close > kc_lower AND 현재봉 close < kc_lower (하단 붕괴)
  - confidence: close > kc_upper * 1.005 → HIGH else MEDIUM
  - 최소 행: 25
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_PERIOD = 20
_ATR_PERIOD = 14
_ATR_MULT = 2.0
_HIGH_CONF_FACTOR = 1.005


def _calc_atr(df: pd.DataFrame, period: int = _ATR_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


class KeltnerBreakoutStrategy(BaseStrategy):
    name = "keltner_breakout"

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

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            if df is None:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=0.0,
                    reasoning="Insufficient data (minimum 25 rows required)",
                    invalidation="",
                )
            return self._hold(df, "Insufficient data (minimum 25 rows required)")

        # idx = last completed candle (iloc[-2])
        idx = len(df) - 2

        # work on completed candles only
        work = df.iloc[: len(df) - 1]

        ema20 = work["close"].ewm(span=_EMA_PERIOD, adjust=False).mean()
        atr14 = _calc_atr(work, _ATR_PERIOD)
        kc_upper = ema20 + _ATR_MULT * atr14
        kc_lower = ema20 - _ATR_MULT * atr14

        # current = idx in work = len(work)-1 = -1
        # prev    = idx-1 in work = len(work)-2 = -2
        curr_close = float(work["close"].iloc[-1])
        prev_close = float(work["close"].iloc[-2])
        curr_upper = float(kc_upper.iloc[-1])
        curr_lower = float(kc_lower.iloc[-1])
        prev_upper = float(kc_upper.iloc[-2])
        prev_lower = float(kc_lower.iloc[-2])
        curr_ema = float(ema20.iloc[-1])
        curr_atr = float(atr14.iloc[-1])

        if pd.isna(curr_upper) or pd.isna(curr_lower) or pd.isna(curr_atr):
            return self._hold(df, "Insufficient data (minimum 25 rows required)")

        entry = float(df["close"].iloc[idx])

        context = (
            f"close={curr_close:.2f} ema20={curr_ema:.2f} "
            f"kc_upper={curr_upper:.2f} kc_lower={curr_lower:.2f} "
            f"atr14={curr_atr:.4f}"
        )

        # BUY: 상단 돌파
        if prev_close < prev_upper and curr_close > curr_upper:
            confidence = (
                Confidence.HIGH
                if curr_close > curr_upper * _HIGH_CONF_FACTOR
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Keltner 상단 돌파: prev_close({prev_close:.2f}) < "
                    f"prev_upper({prev_upper:.2f}), "
                    f"curr_close({curr_close:.2f}) > kc_upper({curr_upper:.2f})"
                ),
                invalidation=f"close가 kc_upper({curr_upper:.2f}) 아래로 복귀 시 무효",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 하단 붕괴
        if prev_close > prev_lower and curr_close < curr_lower:
            confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Keltner 하단 붕괴: prev_close({prev_close:.2f}) > "
                    f"prev_lower({prev_lower:.2f}), "
                    f"curr_close({curr_close:.2f}) < kc_lower({curr_lower:.2f})"
                ),
                invalidation=f"close가 kc_lower({curr_lower:.2f}) 위로 복귀 시 무효",
                bull_case=context,
                bear_case=context,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Keltner 채널 내부 (HOLD). {context}",
            invalidation="N/A",
        )
