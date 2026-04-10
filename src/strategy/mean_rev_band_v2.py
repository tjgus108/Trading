"""
MeanRevBandV2Strategy:
- ATR 기반 동적 밴드 (Keltner-like, EMA20 ± N*ATR14)
- BUY:  close < band2_dn AND close > band2_dn.prev  (밴드2 아래서 복귀)
        OR (close < band1_dn AND close > prev_close)
- SELL: close > band2_up AND close < band2_up.prev
        OR (close > band1_up AND close < prev_close)
- confidence: HIGH if band2 조건, else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EMA_SPAN = 20
_ATR_PERIOD = 14
_BAND1_MULT = 1.0
_BAND2_MULT = 2.0


def _calc_atr(df: pd.DataFrame, period: int) -> pd.Series:
    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


class MeanRevBandV2Strategy(BaseStrategy):
    name = "mean_rev_band_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for mean_rev_band_v2")

        close = df["close"]
        ema20 = close.ewm(span=_EMA_SPAN, adjust=False).mean()
        atr14 = _calc_atr(df, _ATR_PERIOD)

        band1_up = ema20 + _BAND1_MULT * atr14
        band1_dn = ema20 - _BAND1_MULT * atr14
        band2_up = ema20 + _BAND2_MULT * atr14
        band2_dn = ema20 - _BAND2_MULT * atr14

        idx = len(df) - 2

        # NaN 체크
        if (
            pd.isna(atr14.iloc[idx])
            or pd.isna(band2_up.iloc[idx])
            or pd.isna(band2_dn.iloc[idx])
        ):
            return self._hold(df, "Insufficient data for mean_rev_band_v2 (NaN)")

        curr_close = float(df["close"].iloc[idx])
        prev_close_val = float(df["close"].iloc[idx - 1])

        b1_up = float(band1_up.iloc[idx])
        b1_dn = float(band1_dn.iloc[idx])
        b2_up = float(band2_up.iloc[idx])
        b2_dn = float(band2_dn.iloc[idx])
        b2_up_prev = float(band2_up.iloc[idx - 1])
        b2_dn_prev = float(band2_dn.iloc[idx - 1])

        context = (
            f"close={curr_close:.4f} ema={float(ema20.iloc[idx]):.4f} "
            f"band1=[{b1_dn:.4f},{b1_up:.4f}] band2=[{b2_dn:.4f},{b2_up:.4f}]"
        )

        # BUY 조건
        buy_band2 = curr_close < b2_dn and curr_close > b2_dn_prev
        buy_band1 = curr_close < b1_dn and curr_close > prev_close_val

        if buy_band2 or buy_band1:
            confidence = Confidence.HIGH if buy_band2 else Confidence.MEDIUM
            if buy_band2:
                reason_detail = (
                    f"band2 아래 복귀: close({curr_close:.4f})<band2_dn({b2_dn:.4f}) "
                    f"AND close>band2_dn_prev({b2_dn_prev:.4f})"
                )
            else:
                reason_detail = (
                    f"band1 아래 반등: close({curr_close:.4f})<band1_dn({b1_dn:.4f}) "
                    f"AND close({curr_close:.4f})>prev_close({prev_close_val:.4f})"
                )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=reason_detail,
                invalidation=f"close < band2_dn ({b2_dn:.4f}) 지속",
                bull_case=context,
                bear_case=context,
            )

        # SELL 조건
        sell_band2 = curr_close > b2_up and curr_close < b2_up_prev
        sell_band1 = curr_close > b1_up and curr_close < prev_close_val

        if sell_band2 or sell_band1:
            confidence = Confidence.HIGH if sell_band2 else Confidence.MEDIUM
            if sell_band2:
                reason_detail = (
                    f"band2 위 복귀: close({curr_close:.4f})>band2_up({b2_up:.4f}) "
                    f"AND close<band2_up_prev({b2_up_prev:.4f})"
                )
            else:
                reason_detail = (
                    f"band1 위 반락: close({curr_close:.4f})>band1_up({b1_up:.4f}) "
                    f"AND close({curr_close:.4f})<prev_close({prev_close_val:.4f})"
                )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=reason_detail,
                invalidation=f"close > band2_up ({b2_up:.4f}) 지속",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        close = float(df["close"].iloc[idx])
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
