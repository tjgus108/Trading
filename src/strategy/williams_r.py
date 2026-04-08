"""
Williams %R 전략:
- %R = (highest_high_14 - close) / (highest_high_14 - lowest_low_14) * -100
- BUY:  %R < -80 AND %R > 전봉 %R (과매도 반등)
- SELL: %R > -20 AND %R < 전봉 %R (과매수 반락)
- confidence: HIGH(%R < -90 or %R > -10), MEDIUM(%R < -80 or %R > -20)
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_PERIOD = 14
_OVERSOLD = -80.0
_OVERBOUGHT = -20.0
_HIGH_OVERSOLD = -90.0
_HIGH_OVERBOUGHT = -10.0


def _williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = _PERIOD) -> pd.Series:
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    denom = hh - ll
    wr = (hh - close) / denom.where(denom != 0, other=float("nan")) * -100
    return wr


class WilliamsRStrategy(BaseStrategy):
    name = "williams_r"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        wr = _williams_r(df["high"], df["low"], df["close"])

        # _last() → iloc[-2] (완성된 마지막 봉)
        curr_wr = float(wr.iloc[-2])
        prev_wr = float(wr.iloc[-3])

        if pd.isna(curr_wr) or pd.isna(prev_wr):
            return self._hold(df, "Williams %R: NaN (데이터 부족)")

        last = self._last(df)
        close = float(last["close"])
        context = f"close={close:.2f} wr={curr_wr:.2f} prev_wr={prev_wr:.2f}"

        # BUY: 과매도(%R < -80) AND 반등(curr > prev)
        if curr_wr < _OVERSOLD and curr_wr > prev_wr:
            confidence = Confidence.HIGH if curr_wr < _HIGH_OVERSOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Williams %R 과매도 반등: wr={curr_wr:.2f}<{_OVERSOLD}, prev={prev_wr:.2f}",
                invalidation=f"%R 재하락 또는 %R >= {_OVERSOLD}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 과매수(%R > -20) AND 반락(curr < prev)
        if curr_wr > _OVERBOUGHT and curr_wr < prev_wr:
            confidence = Confidence.HIGH if curr_wr > _HIGH_OVERBOUGHT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Williams %R 과매수 반락: wr={curr_wr:.2f}>{_OVERBOUGHT}, prev={prev_wr:.2f}",
                invalidation=f"%R 재상승 또는 %R <= {_OVERBOUGHT}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: wr={curr_wr:.2f} prev={prev_wr:.2f}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
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
