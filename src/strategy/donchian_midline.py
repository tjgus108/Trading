"""
DonchianMidlineStrategy: Donchian Channel 중선 크로스 + EMA50 추세 필터.

로직:
  - Donchian Channel: upper=high.rolling(20).max(), lower=low.rolling(20).min()
  - Midline = (upper + lower) / 2
  - BUY:  close crosses above midline (prev <= mid, now > mid) AND close > EMA50
  - SELL: close crosses below midline (prev >= mid, now < mid) AND close < EMA50
  - confidence: close > upper * 0.98 (상단 근접) → HIGH for BUY
                close < lower * 1.02 (하단 근접) → HIGH for SELL
  - 최소 행: 55
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_PERIOD = 20
_EMA_PERIOD = 50


def _calc_indicators(df: pd.DataFrame):
    """완성 캔들(-2) 기준 지표 계산. (upper, lower, mid, ema50) x (prev, last)"""
    # 진행 중 캔들(-1) 제외한 완성 캔들
    completed = df.iloc[:-1]

    upper = completed["high"].rolling(_PERIOD).max()
    lower = completed["low"].rolling(_PERIOD).min()
    mid = (upper + lower) / 2.0
    ema50 = completed["close"].ewm(span=_EMA_PERIOD, adjust=False).mean()

    # 신호 봉 = -1 (completed 기준), 이전 봉 = -2
    last_upper = float(upper.iloc[-1])
    last_lower = float(lower.iloc[-1])
    last_mid = float(mid.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_close = float(completed["close"].iloc[-1])

    prev_mid = float(mid.iloc[-2])
    prev_close = float(completed["close"].iloc[-2])

    return (last_upper, last_lower, last_mid, last_ema50,
            last_close, prev_mid, prev_close)


class DonchianMidlineStrategy(BaseStrategy):
    name = "donchian_midline"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        (upper, lower, mid, ema50,
         close, prev_mid, prev_close) = _calc_indicators(df)

        crosses_above = prev_close <= prev_mid and close > mid
        crosses_below = prev_close >= prev_mid and close < mid
        trend_bull = close > ema50
        trend_bear = close < ema50

        context = (
            f"close={close:.4f} mid={mid:.4f} upper={upper:.4f} "
            f"lower={lower:.4f} ema50={ema50:.4f}"
        )

        if crosses_above and trend_bull:
            near_upper = close > upper * 0.98
            conf = Confidence.HIGH if near_upper else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Close crossed above Donchian midline. {context}. "
                    f"NearUpper={near_upper}"
                ),
                invalidation=f"Close back below midline ({mid:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if crosses_below and trend_bear:
            near_lower = close < lower * 1.02
            conf = Confidence.HIGH if near_lower else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Close crossed below Donchian midline. {context}. "
                    f"NearLower={near_lower}"
                ),
                invalidation=f"Close back above midline ({mid:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No midline crossover. {context}")

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
