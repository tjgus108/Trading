"""
MACDSlopeStrategy:
- 기존 macd_strategy.py(히스토그램 zero-cross)와 차별화: 히스토그램 기울기 기반
- MACD histogram = (EMA12 - EMA26) - Signal9
- hist_slope = hist - hist.shift(3)         (3봉 기울기)
- slope_acceleration = hist_slope - hist_slope.shift(3)  (가속도)
- BUY:  hist < 0 AND hist_slope > 0 AND slope_acceleration > 0
        (음수 영역에서 가속 회복)
- SELL: hist > 0 AND hist_slope < 0 AND slope_acceleration < 0
        (양수 영역에서 가속 하락)
- confidence: |slope_acceleration| > slope_acceleration.rolling(20).std() → HIGH
- 최소 행: 35
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_EMA_FAST = 12
_EMA_SLOW = 26
_EMA_SIGNAL = 9
_SLOPE_PERIOD = 3
_STD_WINDOW = 20


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


class MACDSlopeStrategy(BaseStrategy):
    name = "macd_slope"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족")

        close = df["close"]
        macd_line = _ema(close, _EMA_FAST) - _ema(close, _EMA_SLOW)
        signal_line = _ema(macd_line, _EMA_SIGNAL)
        histogram = macd_line - signal_line

        hist_slope = histogram - histogram.shift(_SLOPE_PERIOD)
        slope_accel = hist_slope - hist_slope.shift(_SLOPE_PERIOD)

        # 마지막 완성봉 (-2)
        hist_now = float(histogram.iloc[-2])
        slope_now = float(hist_slope.iloc[-2])
        accel_now = float(slope_accel.iloc[-2])
        close_now = float(close.iloc[-2])

        # NaN 체크
        if accel_now != accel_now:
            return self._hold(df, "데이터 부족 (NaN)")

        # confidence: 가속도 vs 20봉 표준편차
        accel_std_window = slope_accel.iloc[-_STD_WINDOW - 2:-2]
        accel_std = float(accel_std_window.std()) if len(accel_std_window) >= 2 else 0.0
        if accel_std > 0 and abs(accel_now) > accel_std:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        context = (
            f"close={close_now:.2f} hist={hist_now:.6f} "
            f"hist_slope={slope_now:.6f} slope_accel={accel_now:.6f}"
        )

        # BUY: 음수 영역에서 가속 회복
        if hist_now < 0 and slope_now > 0 and accel_now > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MACD Slope BUY: hist({hist_now:.6f})<0, "
                    f"hist_slope({slope_now:.6f})>0, "
                    f"slope_accel({accel_now:.6f})>0 — 음수영역 가속 회복"
                ),
                invalidation="hist_slope < 0 또는 slope_acceleration < 0으로 전환",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 양수 영역에서 가속 하락
        if hist_now > 0 and slope_now < 0 and accel_now < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"MACD Slope SELL: hist({hist_now:.6f})>0, "
                    f"hist_slope({slope_now:.6f})<0, "
                    f"slope_accel({accel_now:.6f})<0 — 양수영역 가속 하락"
                ),
                invalidation="hist_slope > 0 또는 slope_acceleration > 0으로 전환",
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
