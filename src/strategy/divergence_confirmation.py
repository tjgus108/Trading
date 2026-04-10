"""
DivergenceConfirmationStrategy:
- 가격과 RSI(14) divergence 탐지
- Bullish: price[-lookback] > price[idx] AND rsi[idx] > rsi[idx-lookback]
- Bearish: price[-lookback] < price[idx] AND rsi[idx] < rsi[idx-lookback]
- confidence: HIGH if RSI <= 30 (bullish) 또는 RSI >= 70 (bearish) else MEDIUM
- 최소 데이터: 30행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_RSI_PERIOD = 14
_LOOKBACK = 10
_RSI_OVERSOLD = 30
_RSI_OVERBOUGHT = 70


def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(period, min_periods=1).mean()
    rs = gain / loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


class DivergenceConfirmationStrategy(BaseStrategy):
    name = "divergence_confirmation"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        completed = df.iloc[: idx + 1]
        price = completed["close"]
        rsi = _calc_rsi(price, _RSI_PERIOD)

        p_now = float(price.iloc[idx])
        p_prev = float(price.iloc[idx - _LOOKBACK])
        r_now = float(rsi.iloc[idx])
        r_prev = float(rsi.iloc[idx - _LOOKBACK])

        context = (
            f"price_now={p_now:.4f} price_prev={p_prev:.4f} "
            f"rsi_now={r_now:.2f} rsi_prev={r_prev:.2f}"
        )

        # Bullish divergence: 가격 하락 but RSI 상승
        if p_now < p_prev and r_now > r_prev:
            confidence = Confidence.HIGH if r_now <= _RSI_OVERSOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=p_now,
                reasoning=f"Bullish divergence (가격↓ RSI↑): {context}",
                invalidation=f"close < {p_now * 0.99:.4f}",
                bull_case=f"RSI={r_now:.2f} 반등 신호",
                bear_case="divergence 실패 시 하락 지속",
            )

        # Bearish divergence: 가격 상승 but RSI 하락
        if p_now > p_prev and r_now < r_prev:
            confidence = Confidence.HIGH if r_now >= _RSI_OVERBOUGHT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=p_now,
                reasoning=f"Bearish divergence (가격↑ RSI↓): {context}",
                invalidation=f"close > {p_now * 1.01:.4f}",
                bull_case="divergence 실패 시 상승 지속",
                bear_case=f"RSI={r_now:.2f} 하락 신호",
            )

        return self._hold(df, f"No divergence: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if len(df) < 2:
            entry = 0.0
        else:
            last = self._last(df) if len(df) >= 2 else df.iloc[-1]
            entry = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
