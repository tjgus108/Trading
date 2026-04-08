"""
MACD 전략:
- MACD  = EMA12 - EMA26 (close 기준)
- Signal = MACD의 EMA9
- Histogram = MACD - Signal
- BUY:  histogram 음수→양수 전환 (현재>0, 전봉<0) AND MACD > 0
- SELL: histogram 양수→음수 전환 (현재<0, 전봉>0) AND MACD < 0
- confidence: HIGH(|histogram| > histogram 20봉 std), MEDIUM 그 외
- 최소 데이터: 35행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_EMA_FAST = 12
_EMA_SLOW = 26
_EMA_SIGNAL = 9
_STD_WINDOW = 20


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


class MACDStrategy(BaseStrategy):
    name = "macd"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        macd_line = _ema(close, _EMA_FAST) - _ema(close, _EMA_SLOW)
        signal_line = _ema(macd_line, _EMA_SIGNAL)
        histogram = macd_line - signal_line

        # 마지막 완성 캔들 인덱스 (-2)
        hist_now = float(histogram.iloc[-2])
        hist_prev = float(histogram.iloc[-3])
        macd_now = float(macd_line.iloc[-2])
        close_now = float(df["close"].iloc[-2])

        # confidence: 20봉 std 기준
        hist_std = float(histogram.iloc[-_STD_WINDOW - 2:-2].std())
        if hist_std > 0 and abs(hist_now) > hist_std:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        context = (
            f"close={close_now:.2f} macd={macd_now:.6f} "
            f"hist={hist_now:.6f} hist_prev={hist_prev:.6f}"
        )

        # BUY: histogram 음→양 전환 AND MACD > 0
        if hist_now > 0 and hist_prev < 0 and macd_now > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MACD histogram 음→양 전환: hist={hist_now:.6f}(전봉 {hist_prev:.6f}), "
                    f"macd={macd_now:.6f}>0"
                ),
                invalidation="Histogram이 다시 음수로 전환되거나 MACD < 0",
                bull_case=context,
                bear_case=context,
            )

        # SELL: histogram 양→음 전환 AND MACD < 0
        if hist_now < 0 and hist_prev > 0 and macd_now < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MACD histogram 양→음 전환: hist={hist_now:.6f}(전봉 {hist_prev:.6f}), "
                    f"macd={macd_now:.6f}<0"
                ),
                invalidation="Histogram이 다시 양수로 전환되거나 MACD > 0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        close_now = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_now,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
