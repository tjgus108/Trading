"""
TRIX Signal Cross 전략:
  EMA1 = EWM(close, span=15)
  EMA2 = EWM(EMA1, span=15)
  EMA3 = EWM(EMA2, span=15)
  trix = (EMA3 - EMA3.shift(1)) / EMA3.shift(1) * 100
  signal = EWM(trix, span=9)
  histogram = trix - signal

BUY:  histogram > 0 AND 이전봉 histogram < 0 (크로스업)
SELL: histogram < 0 AND 이전봉 histogram > 0 (크로스다운)
confidence: HIGH if |histogram| > std(histogram, 20), MEDIUM 그 외
최소 데이터: 50행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal
from typing import Optional

_PERIOD = 15
_SIGNAL_PERIOD = 9
_STD_WINDOW = 20
_MIN_ROWS = 50


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _calc_trix_signal(close: pd.Series):
    """histogram = trix - signal 계산."""
    ema1 = _ema(close, _PERIOD)
    ema2 = _ema(ema1, _PERIOD)
    ema3 = _ema(ema2, _PERIOD)
    trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100
    signal = _ema(trix, _SIGNAL_PERIOD)
    histogram = trix - signal
    return trix, signal, histogram


class TRIXSignalStrategy(BaseStrategy):
    name = "trix_signal"

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

        trix, signal_line, histogram = _calc_trix_signal(df["close"])

        idx = len(df) - 2  # _last() 패턴
        hist_now = float(histogram.iloc[idx])
        hist_prev = float(histogram.iloc[idx - 1])
        trix_now = float(trix.iloc[idx])
        sig_now = float(signal_line.iloc[idx])
        entry = float(df["close"].iloc[idx])

        # std window: 인덱스 기준 최근 _STD_WINDOW 개
        hist_std = float(histogram.iloc[max(0, idx - _STD_WINDOW + 1): idx + 1].std())

        context = (
            f"TRIX={trix_now:.4f} Signal={sig_now:.4f} "
            f"Hist={hist_now:.4f} HStd={hist_std:.4f}"
        )

        confidence = (
            Confidence.HIGH if abs(hist_now) > hist_std else Confidence.MEDIUM
        )

        # BUY: histogram 크로스업 (음→양)
        if hist_now > 0 and hist_prev < 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TRIX Signal 크로스업: {context}",
                invalidation="histogram이 다시 0 하향 돌파 시",
                bull_case=f"histogram {hist_prev:.4f} → {hist_now:.4f}, 모멘텀 전환",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: histogram 크로스다운 (양→음)
        if hist_now < 0 and hist_prev > 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TRIX Signal 크로스다운: {context}",
                invalidation="histogram이 다시 0 상향 돌파 시",
                bull_case="단기 조정일 수 있음",
                bear_case=f"histogram {hist_prev:.4f} → {hist_now:.4f}, 하락 전환",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"TRIX Signal 중립: {context}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
