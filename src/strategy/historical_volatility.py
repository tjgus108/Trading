"""
HistoricalVolatilityStrategy: 역사적 변동성 기반 전략.

- Log Returns = ln(close / prev_close)
- HV20 = std(Log Returns, 20) * sqrt(252) * 100  (연환산 변동성 %)
- HV5  = std(Log Returns, 5)  * sqrt(252) * 100  (단기)
- BUY:  HV5 < HV20 * 0.7 AND close > ema50  (변동성 수축 + 상승 추세)
- SELL: HV5 < HV20 * 0.7 AND close < ema50  (변동성 수축 + 하락 추세)
- HOLD: HV5 >= HV20 * 0.7 (변동성 확장 중)
- confidence: HIGH if ratio < 0.5, MEDIUM if ratio < 0.7
- 최소 30행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_CONTRACTION_MED = 0.7
_CONTRACTION_HIGH = 0.5


class HistoricalVolatilityStrategy(BaseStrategy):
    name = "historical_volatility"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        log_ret = np.log(df["close"] / df["close"].shift(1))
        hv20 = log_ret.rolling(20).std() * np.sqrt(252) * 100
        hv5 = log_ret.rolling(5).std() * np.sqrt(252) * 100

        hv20_now = float(hv20.iloc[idx])
        hv5_now = float(hv5.iloc[idx])
        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        ratio = hv5_now / max(hv20_now, 1e-10)

        context = (
            f"close={close:.2f} ema50={ema50:.2f} "
            f"HV5={hv5_now:.2f} HV20={hv20_now:.2f} ratio={ratio:.3f}"
        )

        if ratio < _CONTRACTION_MED:
            confidence = Confidence.HIGH if ratio < _CONTRACTION_HIGH else Confidence.MEDIUM
            if close > ema50:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"HV Contraction BUY: ratio={ratio:.3f}<{_CONTRACTION_MED}, "
                        f"close({close:.2f})>ema50({ema50:.2f})"
                    ),
                    invalidation=f"ratio>={_CONTRACTION_MED} or close<ema50({ema50:.2f})",
                    bull_case=context,
                    bear_case=context,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"HV Contraction SELL: ratio={ratio:.3f}<{_CONTRACTION_MED}, "
                        f"close({close:.2f})<ema50({ema50:.2f})"
                    ),
                    invalidation=f"ratio>={_CONTRACTION_MED} or close>ema50({ema50:.2f})",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No signal: HV expanding ratio={ratio:.3f}>={_CONTRACTION_MED}", context, context)

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
