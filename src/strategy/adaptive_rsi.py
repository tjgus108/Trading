"""
AdaptiveRSIStrategy: Kaufman Adaptive RSI 기반 전략.
- KAMA (Kaufman Adaptive Moving Average) 계산 후 close vs KAMA로 추세 판단
- RSI(close, 14) 기반 과매수/과매도 필터
- BUY:  close > KAMA AND RSI14 < 40
- SELL: close < KAMA AND RSI14 > 60
- confidence: HIGH if RSI < 30 (BUY) or RSI > 70 (SELL), MEDIUM otherwise
- 최소 데이터: 30행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_ER_PERIOD = 10
_RSI_PERIOD = 14
_FAST_SC = 2 / (2 + 1)
_SLOW_SC = 2 / (30 + 1)


def _rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _calc_kama(df: pd.DataFrame) -> pd.Series:
    er_period = _ER_PERIOD
    direction = df["close"].diff(er_period).abs()
    volatility = df["close"].diff().abs().rolling(er_period).sum()
    er = direction / volatility.replace(0, 1e-10)
    sc = (er * (_FAST_SC - _SLOW_SC) + _SLOW_SC) ** 2

    close_arr = df["close"].values
    sc_arr = sc.values
    kama = np.zeros(len(close_arr))
    kama[0] = close_arr[0]
    for i in range(1, len(close_arr)):
        sc_i = sc_arr[i] if not np.isnan(sc_arr[i]) else _SLOW_SC ** 2
        kama[i] = kama[i - 1] + sc_i * (close_arr[i] - kama[i - 1])
    return pd.Series(kama, index=df.index)


class AdaptiveRSIStrategy(BaseStrategy):
    name = "adaptive_rsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        kama_series = _calc_kama(df)
        rsi = _rsi(df["close"], _RSI_PERIOD)

        close = float(df["close"].iloc[idx])
        kama_val = float(kama_series.iloc[idx])
        rsi_val = float(rsi.iloc[idx])

        if np.isnan(rsi_val):
            return self._hold(df, "RSI NaN — 데이터 부족")

        context = f"close={close:.2f} kama={kama_val:.2f} rsi={rsi_val:.2f}"

        if close > kama_val and rsi_val < 40:
            confidence = Confidence.HIGH if rsi_val < 30 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Adaptive RSI BUY: close({close:.2f})>KAMA({kama_val:.2f}), RSI={rsi_val:.2f}<40",
                invalidation=f"close < KAMA({kama_val:.2f}) or RSI > 40",
                bull_case=context,
                bear_case=context,
            )

        if close < kama_val and rsi_val > 60:
            confidence = Confidence.HIGH if rsi_val > 70 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Adaptive RSI SELL: close({close:.2f})<KAMA({kama_val:.2f}), RSI={rsi_val:.2f}>60",
                invalidation=f"close > KAMA({kama_val:.2f}) or RSI < 60",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
