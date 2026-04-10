"""
AdaptiveThresholdStrategy:
- 원리: 최근 변동성(ATR)에 따라 동적으로 조정되는 임계값 사용
- 지표:
  - atr14 = rolling ATR(14)
  - norm_price = (close - close.rolling(20).mean()) / atr14
  - threshold_up = norm_price.rolling(20).quantile(0.8)
  - threshold_down = norm_price.rolling(20).quantile(0.2)
- 신호:
  - BUY: norm_price crosses above threshold_up
  - SELL: norm_price crosses below threshold_down
  - HOLD: 그 외
- confidence: HIGH if norm_price > threshold_up * 1.2 else MEDIUM
- 최소 데이터: 40행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_ATR_PERIOD = 14
_NORM_PERIOD = 20
_QUANT_UP = 0.8
_QUANT_DOWN = 0.2
_HIGH_CONF_MULT = 1.2


def _compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


class AdaptiveThresholdStrategy(BaseStrategy):
    name = "adaptive_threshold"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = (
                f"Insufficient data: need {_MIN_ROWS} rows, got {0 if df is None else len(df)}"
            )
            if df is None:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=0.0,
                    reasoning=reason,
                    invalidation="",
                    bull_case="",
                    bear_case="",
                )
            return self._hold(df, reason)

        atr14 = _compute_atr(df, _ATR_PERIOD)
        close_ma = df["close"].rolling(_NORM_PERIOD).mean()
        norm_price = (df["close"] - close_ma) / atr14

        threshold_up = norm_price.rolling(_NORM_PERIOD).quantile(_QUANT_UP)
        threshold_down = norm_price.rolling(_NORM_PERIOD).quantile(_QUANT_DOWN)

        idx = len(df) - 2

        np_curr = norm_price.iloc[idx]
        np_prev = norm_price.iloc[idx - 1]
        tu_curr = threshold_up.iloc[idx]
        td_curr = threshold_down.iloc[idx]

        # NaN 처리
        if any(
            v is None or (isinstance(v, float) and np.isnan(v))
            for v in [np_curr, np_prev, tu_curr, td_curr]
        ):
            return self._hold(df, "NaN in indicators — waiting for sufficient history")

        close_curr = float(df["close"].iloc[idx])

        context = (
            f"norm_price={np_curr:.4f} prev={np_prev:.4f} "
            f"thresh_up={tu_curr:.4f} thresh_down={td_curr:.4f}"
        )

        # BUY: crossover above threshold_up
        if np_prev < tu_curr and np_curr >= tu_curr:
            confidence = (
                Confidence.HIGH if np_curr > tu_curr * _HIGH_CONF_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"adaptive_threshold BUY: norm_price crossed above threshold_up "
                    f"({np_prev:.4f} → {np_curr:.4f} >= {tu_curr:.4f})"
                ),
                invalidation=f"norm_price drops below threshold_up ({tu_curr:.4f})",
                bull_case=context,
                bear_case=context,
            )

        # SELL: crossunder below threshold_down
        if np_prev > td_curr and np_curr <= td_curr:
            confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"adaptive_threshold SELL: norm_price crossed below threshold_down "
                    f"({np_prev:.4f} → {np_curr:.4f} <= {td_curr:.4f})"
                ),
                invalidation=f"norm_price rises above threshold_down ({td_curr:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
