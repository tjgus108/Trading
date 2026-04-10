"""
TrendFibonacciStrategy: 피보나치 되돌림 레벨 기반 추세 추종 전략.

로직:
- EMA20 방향으로 추세 판단
- swing high/low 기반 피보나치 레벨 계산
- BUY: 상승추세(ema20 > ema20[-1]) + close < fib_382 (38.2% 되돌림)
- SELL: 하락추세(ema20 < ema20[-1]) + close > fib_618 (61.8% 반등)
- confidence: HIGH if close가 fib_500 근방(±5% range) else MEDIUM
"""

import math
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendFibonacciStrategy(BaseStrategy):
    name = "trend_fibonacci"

    _MIN_ROWS = 25
    _LOOKBACK = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
            )

        idx = len(df) - 2
        last = df.iloc[idx]
        close = df["close"]
        high = df["high"]
        low = df["low"]

        lookback = self._LOOKBACK

        swing_high = high.rolling(lookback, min_periods=1).max()
        swing_low = low.rolling(lookback, min_periods=1).min()
        fib_range = swing_high - swing_low

        fib_382 = swing_high - fib_range * 0.382
        fib_618 = swing_high - fib_range * 0.618
        fib_500 = swing_high - fib_range * 0.500

        ema20 = close.ewm(span=20, adjust=False).mean()

        sh = swing_high.iloc[idx]
        sl = swing_low.iloc[idx]
        fr = fib_range.iloc[idx]
        f382 = fib_382.iloc[idx]
        f618 = fib_618.iloc[idx]
        f500 = fib_500.iloc[idx]
        e20 = ema20.iloc[idx]
        e20_prev = ema20.iloc[idx - 1] if idx > 0 else e20
        c = float(last["close"])

        # NaN 체크
        if any(math.isnan(v) for v in [sh, sl, fr, f382, f618, f500, e20, e20_prev, c]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=c,
                reasoning="NaN 값 감지: HOLD",
                invalidation="",
            )

        uptrend = e20 > e20_prev
        downtrend = e20 < e20_prev

        # confidence: close가 fib_500 근방 ±5% range
        near_fib500 = fr > 0 and abs(c - f500) < fr * 0.05
        conf = Confidence.HIGH if near_fib500 else Confidence.MEDIUM

        bull_case = (
            f"EMA20={e20:.4f} rising, close={c:.4f} < fib_382={f382:.4f}, "
            f"swing_high={sh:.4f}, swing_low={sl:.4f}"
        )
        bear_case = (
            f"EMA20={e20:.4f} falling, close={c:.4f} > fib_618={f618:.4f}, "
            f"swing_high={sh:.4f}, swing_low={sl:.4f}"
        )

        # BUY: 상승추세 + 38.2% 되돌림
        if uptrend and c < f382:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"상승추세(EMA20={e20:.4f} > prev={e20_prev:.4f}) + "
                    f"38.2% 되돌림 (close={c:.4f} < fib_382={f382:.4f}). "
                    f"fib_500={f500:.4f}, near_500={near_fib500}"
                ),
                invalidation=f"Close below swing_low ({sl:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 하락추세 + 61.8% 반등
        if downtrend and c > f618:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"하락추세(EMA20={e20:.4f} < prev={e20_prev:.4f}) + "
                    f"61.8% 반등 (close={c:.4f} > fib_618={f618:.4f}). "
                    f"fib_500={f500:.4f}, near_500={near_fib500}"
                ),
                invalidation=f"Close above swing_high ({sh:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=c,
            reasoning=(
                f"조건 미충족: uptrend={uptrend}, downtrend={downtrend}, "
                f"close={c:.4f}, fib_382={f382:.4f}, fib_618={f618:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
