"""
MACD Histogram Divergence 전략:
- Bullish Divergence (BUY): close 최저, histogram 개선 중 (histogram < 0)
- Bearish Divergence (SELL): close 최고, histogram 악화 중 (histogram > 0)
- confidence: HIGH if |histogram 변화| > std(histogram, 20), MEDIUM 그 외
- 최소 데이터: 40행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_FAST = 12
_SLOW = 26
_SIGNAL = 9
_LOOKBACK = 10
_STD_WINDOW = 20
_CLOSE_TOLERANCE = 0.01   # close가 최저/최고 근처 허용 범위 (1%)
_MIN_ROWS = 40


def _ewm(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


class MACDHistDivStrategy(BaseStrategy):
    name = "macd_hist_div"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_signal(0.0, "데이터 부족")

        close = df["close"].copy()

        macd_line = _ewm(close, _FAST) - _ewm(close, _SLOW)
        signal_line = _ewm(macd_line, _SIGNAL)
        histogram = macd_line - signal_line

        # _last(df) = df.iloc[-2] → 인덱스로는 -2
        last_idx = len(df) - 2   # 마지막 완성 캔들 위치
        entry = float(df["close"].iloc[last_idx])

        hist_now = float(histogram.iloc[last_idx])
        hist_prev = float(histogram.iloc[last_idx - _LOOKBACK])
        close_now = float(close.iloc[last_idx])

        # 최근 10봉 범위 (현재 포함)
        close_window = close.iloc[last_idx - _LOOKBACK: last_idx + 1]
        min10 = float(close_window.min())
        max10 = float(close_window.max())

        # histogram std (최근 20봉)
        hist_window = histogram.iloc[max(0, last_idx - _STD_WINDOW): last_idx + 1]
        hist_std = float(hist_window.std()) if len(hist_window) >= 2 else 0.0

        hist_change = abs(hist_now - hist_prev)
        high_conf = hist_std > 0 and hist_change > hist_std

        bullish = (
            close_now < min10 * (1 + _CLOSE_TOLERANCE)
            and hist_now > hist_prev
            and hist_now < 0
        )
        bearish = (
            close_now > max10 * (1 - _CLOSE_TOLERANCE)
            and hist_now < hist_prev
            and hist_now > 0
        )

        if bullish and not bearish:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"MACD Histogram Bullish Divergence: "
                    f"close={close_now:.4f} min10={min10:.4f}, "
                    f"hist={hist_now:.6f} > hist[-10]={hist_prev:.6f}"
                ),
                invalidation="Histogram이 다시 하락하거나 close 신저점 갱신 시",
                bull_case=f"Histogram 개선 중 ({hist_change:.6f})",
                bear_case="여전히 histogram 음수 구간",
            )

        if bearish and not bullish:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"MACD Histogram Bearish Divergence: "
                    f"close={close_now:.4f} max10={max10:.4f}, "
                    f"hist={hist_now:.6f} < hist[-10]={hist_prev:.6f}"
                ),
                invalidation="Histogram이 다시 상승하거나 close 신고점 갱신 시",
                bull_case="여전히 histogram 양수 구간",
                bear_case=f"Histogram 약화 중 ({hist_change:.6f})",
            )

        return self._hold_signal(entry, "MACD Histogram Divergence 없음")

    def _hold_signal(self, price: float, reason: str) -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
