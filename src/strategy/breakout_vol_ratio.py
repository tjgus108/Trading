"""
BreakoutVolRatioStrategy:
- 20봉 고점/저점 돌파 + 거래량 비율로 신뢰성 판단
- BUY:  broke_up AND vol_ratio > 1.5
- SELL: broke_down AND vol_ratio > 1.5
- confidence: HIGH if vol_ratio > 2.0 else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 20
_ATR_PERIOD = 14
_VOL_RATIO_THRESH = 1.5
_HIGH_CONF_VOL = 2.0


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


class BreakoutVolRatioStrategy(BaseStrategy):
    name = "breakout_vol_ratio"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for breakout_vol_ratio")

        resistance = df["high"].rolling(_LOOKBACK).max().shift(1)
        support = df["low"].rolling(_LOOKBACK).min().shift(1)
        vol_ma = df["volume"].rolling(_LOOKBACK).mean()
        vol_ratio_series = df["volume"] / vol_ma
        atr14 = _calc_atr(df, _ATR_PERIOD)

        idx = len(df) - 2

        res_val = resistance.iloc[idx]
        sup_val = support.iloc[idx]
        vol_ratio = vol_ratio_series.iloc[idx]
        atr_val = atr14.iloc[idx]
        curr_close = float(df["close"].iloc[idx])

        # NaN 체크
        if (
            pd.isna(res_val)
            or pd.isna(sup_val)
            or pd.isna(vol_ratio)
            or pd.isna(atr_val)
        ):
            return self._hold(df, "Insufficient data for breakout_vol_ratio (NaN)")

        res_val = float(res_val)
        sup_val = float(sup_val)
        vol_ratio = float(vol_ratio)
        atr_val = float(atr_val) if atr_val > 0 else 1e-10

        broke_up = curr_close > res_val
        broke_down = curr_close < sup_val
        strong_vol = vol_ratio > _VOL_RATIO_THRESH

        breakout_size_up = (curr_close - res_val) / atr_val if broke_up else 0.0
        breakout_size_dn = (sup_val - curr_close) / atr_val if broke_down else 0.0

        context = (
            f"close={curr_close:.4f} resistance={res_val:.4f} support={sup_val:.4f} "
            f"vol_ratio={vol_ratio:.3f} atr={atr_val:.4f}"
        )

        if broke_up and strong_vol:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_VOL else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"상향 돌파: close({curr_close:.4f})>resistance({res_val:.4f}), "
                    f"vol_ratio={vol_ratio:.3f}>{_VOL_RATIO_THRESH}, "
                    f"breakout_size={breakout_size_up:.3f}ATR"
                ),
                invalidation=f"close < resistance ({res_val:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if broke_down and strong_vol:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_VOL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"하향 돌파: close({curr_close:.4f})<support({sup_val:.4f}), "
                    f"vol_ratio={vol_ratio:.3f}>{_VOL_RATIO_THRESH}, "
                    f"breakout_size={breakout_size_dn:.3f}ATR"
                ),
                invalidation=f"close > support ({sup_val:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No breakout or insufficient vol: {context}", context, context)

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
