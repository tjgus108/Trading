"""
AutoCorrelationStrategy: 가격 수익률의 자기상관(AutoCorrelation) 기반 전략.
- Positive AC (> 0.1): 추세 지속성 → Trend following
- Negative AC (< -0.1): 평균 회귀 → Mean reversion
- BUY (trend): AC > 0.1 AND close > prev_close
- BUY (reversion): AC < -0.1 AND close < SMA20 * 0.98
- SELL (trend): AC > 0.1 AND close < prev_close
- SELL (reversion): AC < -0.1 AND close > SMA20 * 1.02
- confidence: |AC| > 0.3 → HIGH
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_ROLL = 20


def _calc_autocorr(close: pd.Series) -> pd.Series:
    returns = close.pct_change()
    lag1 = returns.shift(1)
    # rolling correlation between returns and lag1
    ac = returns.rolling(_ROLL).corr(lag1)
    return ac


class AutoCorrelationStrategy(BaseStrategy):
    name = "autocorr_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        close_series = df["close"]

        ac_series = _calc_autocorr(close_series)
        sma20 = close_series.rolling(_ROLL).mean()

        ac_val = float(ac_series.iloc[idx])
        close = float(close_series.iloc[idx])
        prev_close = float(close_series.iloc[idx - 1])
        sma_val = float(sma20.iloc[idx])

        if np.isnan(ac_val) or np.isnan(sma_val):
            return self._hold(df, "AC or SMA NaN — 데이터 부족")

        abs_ac = abs(ac_val)
        confidence = Confidence.HIGH if abs_ac > 0.3 else Confidence.MEDIUM
        context = f"AC={ac_val:.3f} close={close:.2f} sma20={sma_val:.2f}"

        # Trend following (positive AC)
        if ac_val > 0.1 and close > prev_close:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AutoCorr BUY(trend): AC={ac_val:.3f}>0.1, close({close:.2f})>prev({prev_close:.2f})",
                invalidation=f"AC <= 0.1 or close < prev_close",
                bull_case=context,
                bear_case=context,
            )

        if ac_val > 0.1 and close < prev_close:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AutoCorr SELL(trend): AC={ac_val:.3f}>0.1, close({close:.2f})<prev({prev_close:.2f})",
                invalidation=f"AC <= 0.1 or close > prev_close",
                bull_case=context,
                bear_case=context,
            )

        # Mean reversion (negative AC)
        if ac_val < -0.1 and close < sma_val * 0.98:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AutoCorr BUY(reversion): AC={ac_val:.3f}<-0.1, close({close:.2f})<SMA20*0.98({sma_val*0.98:.2f})",
                invalidation=f"close > SMA20({sma_val:.2f})",
                bull_case=context,
                bear_case=context,
            )

        if ac_val < -0.1 and close > sma_val * 1.02:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"AutoCorr SELL(reversion): AC={ac_val:.3f}<-0.1, close({close:.2f})>SMA20*1.02({sma_val*1.02:.2f})",
                invalidation=f"close < SMA20({sma_val:.2f})",
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
