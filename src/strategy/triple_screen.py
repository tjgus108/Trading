"""
TripleScreenStrategy: Alexander Elder's Triple Screen.

Screen 1 (Tide):  EMA26 기울기로 장기 추세
  - Bullish tide:  ema26[-1] > ema26[-2]
  - Bearish tide:  ema26[-1] < ema26[-2]

Screen 2 (Wave):  Stochastic으로 역방향 파동
  - Bullish tide → stoch_k < 30 (pullback)
  - Bearish tide → stoch_k > 70 (rally)

Screen 3 (Ripple): 현재 캔들 방향 확인
  - BUY:  bullish tide + stoch_k < 30 + close > open (양봉)
  - SELL: bearish tide + stoch_k > 70 + close < open (음봉)

confidence:
  - BUY:  stoch_k < 20 → HIGH
  - SELL: stoch_k > 80 → HIGH
  - 나머지 → MEDIUM

최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_EMA_PERIOD = 26
_STOCH_PERIOD = 14


def _calc_ema26(series: pd.Series) -> pd.Series:
    return series.ewm(span=_EMA_PERIOD, adjust=False).mean()


def _calc_stoch_k(df: pd.DataFrame, period: int = _STOCH_PERIOD) -> float:
    """완성 캔들(-2) 기준 Stochastic %K 계산."""
    # 진행 중 캔들(-1) 제외
    window = df.iloc[:-1]
    if len(window) < period:
        return 50.0

    closes = window["close"]
    highs = window["high"] if "high" in window.columns else closes
    lows = window["low"] if "low" in window.columns else closes

    # 신호 봉(-1 in completed window) 기준 period 구간
    slice_high = highs.iloc[-period:]
    slice_low = lows.iloc[-period:]
    h = float(slice_high.max())
    lo = float(slice_low.min())
    c = float(closes.iloc[-1])

    denom = h - lo
    if denom == 0:
        return 50.0
    return (c - lo) / denom * 100.0


class TripleScreenStrategy(BaseStrategy):
    name = "triple_screen"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        completed = df.iloc[:-1]
        ema26 = _calc_ema26(completed["close"])

        ema_last = float(ema26.iloc[-1])
        ema_prev = float(ema26.iloc[-2])

        bullish_tide = ema_last > ema_prev
        bearish_tide = ema_last < ema_prev

        stoch_k = _calc_stoch_k(df)

        last = self._last(df)
        close = float(last["close"])
        open_ = float(last["open"])
        is_bull_candle = close > open_
        is_bear_candle = close < open_

        context = (
            f"ema26={ema_last:.4f}(prev={ema_prev:.4f}) "
            f"stoch_k={stoch_k:.1f} close={close:.4f} open={open_:.4f}"
        )

        # BUY: 세 화면 모두 통과
        if bullish_tide and stoch_k < 30 and is_bull_candle:
            conf = Confidence.HIGH if stoch_k < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Triple Screen BUY: bullish tide + stoch_k={stoch_k:.1f}<30 "
                    f"+ bullish candle. {context}"
                ),
                invalidation="EMA26 slope turns bearish or stoch_k > 50",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 세 화면 모두 통과
        if bearish_tide and stoch_k > 70 and is_bear_candle:
            conf = Confidence.HIGH if stoch_k > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Triple Screen SELL: bearish tide + stoch_k={stoch_k:.1f}>70 "
                    f"+ bearish candle. {context}"
                ),
                invalidation="EMA26 slope turns bullish or stoch_k < 50",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No Triple Screen signal. {context}")

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
