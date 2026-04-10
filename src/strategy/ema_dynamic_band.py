"""
EMADynamicBandStrategy: 변동성에 따라 동적으로 조정되는 EMA 밴드.

- EMA20 기반 동적 밴드
- realized volatility percentile로 밴드 폭 조정 (1%~3%)
- BUY: close < lower AND close > lower.shift(1) (하단 밴드 복귀)
- SELL: close > upper AND close < upper.shift(1) (상단 밴드 이탈)
- confidence HIGH: rv_percentile < 0.2 (낮은 변동성)
- 최소 행: 55
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EMADynamicBandStrategy(BaseStrategy):
    name = "ema_dynamic_band"

    MIN_ROWS = 55

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < self.MIN_ROWS:
            close = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="Insufficient data: minimum 55 rows required",
                invalidation="",
            )

        close_series = df["close"]

        ema20 = close_series.ewm(span=20, adjust=False).mean()

        returns = close_series.pct_change()
        rv = returns.rolling(20).std()
        rv_percentile = rv.rolling(50).rank(pct=True)  # 0~1

        band_mult = 0.01 + 0.02 * rv_percentile  # 0.01 ~ 0.03

        upper = ema20 * (1 + band_mult)
        lower = ema20 * (1 - band_mult)

        idx = len(df) - 2  # _last == df.iloc[-2]

        # NaN 체크
        if (
            pd.isna(upper.iloc[idx])
            or pd.isna(lower.iloc[idx])
            or pd.isna(rv_percentile.iloc[idx])
        ):
            close_val = float(close_series.iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="Insufficient data: NaN in indicators",
                invalidation="",
            )

        close_val = float(close_series.iloc[idx])
        close_prev = float(close_series.iloc[idx - 1])
        upper_val = float(upper.iloc[idx])
        lower_val = float(lower.iloc[idx])
        upper_prev = float(upper.iloc[idx - 1])
        lower_prev = float(lower.iloc[idx - 1])
        rv_pct = float(rv_percentile.iloc[idx])
        ema20_val = float(ema20.iloc[idx])

        # Confidence
        conf = Confidence.HIGH if rv_pct < 0.2 else Confidence.MEDIUM

        reasoning_base = (
            f"ema20={ema20_val:.4f} upper={upper_val:.4f} lower={lower_val:.4f} "
            f"close={close_val:.4f} rv_pct={rv_pct:.3f}"
        )

        # BUY: close < lower AND close > lower.shift(1) (하단 밴드 복귀)
        if close_val < lower_val and close_prev > lower_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"EMADynamicBand BUY: price returned above lower band. {reasoning_base}",
                invalidation=f"Close below lower band ({lower_val:.4f})",
            )

        # SELL: close > upper AND close < upper.shift(1) (상단 밴드 이탈 후 반락)
        if close_val > upper_val and close_prev < upper_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"EMADynamicBand SELL: price broke above upper band. {reasoning_base}",
                invalidation=f"Close above upper band ({upper_val:.4f})",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"EMADynamicBand HOLD: no band signal. {reasoning_base}",
            invalidation="",
        )
