"""
TrendFilteredMeanRevStrategy:
- 추세 필터 + 평균 회귀 (추세 방향의 풀백만 진입)
- BUY:  trend_up AND close < lower (상승 추세 + BB 하단 풀백)
- SELL: trend_down AND close > upper (하락 추세 + BB 상단 풀백)
- confidence: HIGH if abs(close - bb_mid) > bb_std * 2.0 else MEDIUM
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_EMA_SPAN = 50
_BB_PERIOD = 20
_BB_STD_MULT = 1.5
_HIGH_STD_MULT = 2.0


class TrendFilteredMeanRevStrategy(BaseStrategy):
    name = "trend_filtered_mean_rev"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        close_series = df["close"]
        ema50 = close_series.ewm(span=_EMA_SPAN, adjust=False).mean()
        bb_mid = close_series.rolling(_BB_PERIOD, min_periods=1).mean()
        bb_std = close_series.rolling(_BB_PERIOD, min_periods=1).std()

        close = float(close_series.iloc[idx])
        ema50_val = float(ema50.iloc[idx])
        bb_mid_val = float(bb_mid.iloc[idx])
        bb_std_val = float(bb_std.iloc[idx]) if not pd.isna(bb_std.iloc[idx]) else 0.0
        upper = bb_mid_val + bb_std_val * _BB_STD_MULT
        lower = bb_mid_val - bb_std_val * _BB_STD_MULT

        if pd.isna(close) or pd.isna(ema50_val) or pd.isna(bb_mid_val):
            return self._hold(df, "NaN in indicators")

        trend_up = close > ema50_val
        trend_down = close < ema50_val

        context = (
            f"close={close:.4f} ema50={ema50_val:.4f} "
            f"bb_mid={bb_mid_val:.4f} upper={upper:.4f} lower={lower:.4f}"
        )

        if trend_up and close < lower:
            deviation = abs(close - bb_mid_val)
            confidence = (
                Confidence.HIGH if deviation > bb_std_val * _HIGH_STD_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"상승 추세 풀백: close({close:.4f})>ema50({ema50_val:.4f}) "
                    f"AND close<lower({lower:.4f})"
                ),
                invalidation=f"close drops below lower band further: {lower:.4f}",
                bull_case=context,
                bear_case=context,
            )

        if trend_down and close > upper:
            deviation = abs(close - bb_mid_val)
            confidence = (
                Confidence.HIGH if deviation > bb_std_val * _HIGH_STD_MULT
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"하락 추세 풀백: close({close:.4f})<ema50({ema50_val:.4f}) "
                    f"AND close>upper({upper:.4f})"
                ),
                invalidation=f"close rises above upper band further: {upper:.4f}",
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
