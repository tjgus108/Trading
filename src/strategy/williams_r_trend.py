"""
WilliamsRTrendStrategy:
- Williams %R = (highest_high_14 - close) / (highest_high_14 - lowest_low_14) * -100
- period = 14
- BUY:  %R crosses above -80 (prev < -80 AND now >= -80) AND EMA20 > EMA50 (uptrend)
- SELL: %R crosses below -20 (prev > -20 AND now <= -20) AND EMA20 < EMA50 (downtrend)
- confidence: HIGH if %R > -90 on BUY or %R < -10 on SELL (extreme reversal)
- 최소 데이터: 55행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_PERIOD = 14
_OVERSOLD = -80.0
_OVERBOUGHT = -20.0
_HIGH_BUY_THRESH = -90.0   # BUY HIGH if curr_wr > -90 (less extreme, cleaner reversal)
_HIGH_SELL_THRESH = -10.0  # SELL HIGH if curr_wr < -10


def _williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = _PERIOD) -> pd.Series:
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    denom = hh - ll
    wr = (hh - close) / denom.where(denom != 0, other=float("nan")) * -100
    return wr


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


class WilliamsRTrendStrategy(BaseStrategy):
    name = "williams_r_trend"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        wr = _williams_r(df["high"], df["low"], df["close"])
        ema20 = _ema(df["close"], 20)
        ema50 = _ema(df["close"], 50)

        curr_wr = float(wr.iloc[-2])
        prev_wr = float(wr.iloc[-3])
        curr_ema20 = float(ema20.iloc[-2])
        curr_ema50 = float(ema50.iloc[-2])

        if pd.isna(curr_wr) or pd.isna(prev_wr):
            return self._hold(df, "Williams %R: NaN (데이터 부족)")

        last = self._last(df)
        close = float(last["close"])
        uptrend = curr_ema20 > curr_ema50
        downtrend = curr_ema20 < curr_ema50
        context = (
            f"close={close:.2f} wr={curr_wr:.2f} prev_wr={prev_wr:.2f} "
            f"ema20={curr_ema20:.2f} ema50={curr_ema50:.2f}"
        )

        # BUY: cross above -80 (prev < -80, now >= -80) AND uptrend
        if prev_wr < _OVERSOLD and curr_wr >= _OVERSOLD and uptrend:
            confidence = Confidence.HIGH if curr_wr > _HIGH_BUY_THRESH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Williams %R 과매도 탈출 + 상승추세: "
                    f"wr={curr_wr:.2f}(prev={prev_wr:.2f}) ema20>ema50"
                ),
                invalidation=f"%R 재하락 또는 EMA20<EMA50",
                bull_case=context,
                bear_case=context,
            )

        # SELL: cross below -20 (prev > -20, now <= -20) AND downtrend
        if prev_wr > _OVERBOUGHT and curr_wr <= _OVERBOUGHT and downtrend:
            confidence = Confidence.HIGH if curr_wr < _HIGH_SELL_THRESH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Williams %R 과매수 이탈 + 하락추세: "
                    f"wr={curr_wr:.2f}(prev={prev_wr:.2f}) ema20<ema50"
                ),
                invalidation=f"%R 재상승 또는 EMA20>EMA50",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

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
