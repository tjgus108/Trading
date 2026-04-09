"""
RSI Momentum Divergence 전략:
- RSI14 계산
- Momentum = close - close.shift(14)
- BUY:  close가 최근 10봉 최저 근처(close < min10 * 1.02) AND RSI14 > 이전 RSI14 (상승 다이버전스)
- SELL: close가 최근 10봉 최고 근처(close > max10 * 0.98) AND RSI14 < 이전 RSI14 (하락 다이버전스)
- confidence: HIGH if |RSI 변화| > 5, MEDIUM 그 외
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_RSI_PERIOD = 14
_LOOKBACK = 10
_HIGH_CONF_RSI_CHANGE = 5.0


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


class RSIMomentumDivStrategy(BaseStrategy):
    name = "rsi_momentum_div"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]
        rsi = _calc_rsi(close, _RSI_PERIOD)
        # momentum = close - close.shift(14)  (계산은 했지만 신호는 RSI 다이버전스 기준)
        # _last(df) = df.iloc[-2] (마지막 완성 캔들)
        last_idx = len(df) - 2  # index of last completed candle

        rsi_now = rsi.iloc[last_idx]
        rsi_prev = rsi.iloc[last_idx - 1]
        close_now = close.iloc[last_idx]

        # 최근 10봉: last_idx-9 ~ last_idx (inclusive)
        window_close = close.iloc[last_idx - _LOOKBACK + 1: last_idx + 1]
        min10 = window_close.min()
        max10 = window_close.max()

        rsi_change = rsi_now - rsi_prev

        near_low = close_now < min10 * 1.02
        near_high = close_now > max10 * 0.98
        rsi_rising = rsi_change > 0
        rsi_falling = rsi_change < 0

        bull_case = f"close {close_now:.2f} near 10-bar low {min10:.2f}, RSI {rsi_prev:.1f}→{rsi_now:.1f}"
        bear_case = f"close {close_now:.2f} near 10-bar high {max10:.2f}, RSI {rsi_prev:.1f}→{rsi_now:.1f}"

        if near_low and rsi_rising:
            conf = Confidence.HIGH if abs(rsi_change) > _HIGH_CONF_RSI_CHANGE else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=float(close_now),
                reasoning=f"RSI Momentum Divergence BUY: close near 10-bar low, RSI 상승 ({rsi_change:+.2f})",
                invalidation="Close below 10-bar low",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if near_high and rsi_falling:
            conf = Confidence.HIGH if abs(rsi_change) > _HIGH_CONF_RSI_CHANGE else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=float(close_now),
                reasoning=f"RSI Momentum Divergence SELL: close near 10-bar high, RSI 하락 ({rsi_change:+.2f})",
                invalidation="Close above 10-bar high",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="다이버전스 조건 미충족",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
