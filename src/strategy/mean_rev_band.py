"""
MeanReversionBandStrategy:
- Adaptive mean reversion using rolling statistics (period=30, std_mult=1.5)
- BUY:  close < lower_band AND close > lower_band.shift(1) (하단 터치 후 회복)
- SELL: close > upper_band AND close < upper_band.shift(1) (상단 터치 후 하락)
- confidence: HIGH if |z_score| > 2.5, else MEDIUM
- 최소 데이터: 35행
- bb_reversion / zscore_mean_reversion과 차별화:
    1.5σ 밴드 + 방향 전환 확인 (이전 캔들 대비 되돌아오는 움직임)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_PERIOD = 30
_STD_MULT = 1.5
_HIGH_CONF_Z = 2.5


class MeanReversionBandStrategy(BaseStrategy):
    name = "mean_rev_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        rolling_mean = close.rolling(_PERIOD).mean()
        rolling_std = close.rolling(_PERIOD).std()
        upper_band = rolling_mean + _STD_MULT * rolling_std
        lower_band = rolling_mean - _STD_MULT * rolling_std

        idx = len(df) - 2  # 마지막 완성 캔들
        close_now = float(close.iloc[idx])
        mean_now = float(rolling_mean.iloc[idx])
        std_now = float(rolling_std.iloc[idx]) or 1e-10
        upper_now = float(upper_band.iloc[idx])
        lower_now = float(lower_band.iloc[idx])
        lower_prev = float(lower_band.iloc[idx - 1])
        upper_prev = float(upper_band.iloc[idx - 1])

        z_score = (close_now - mean_now) / std_now
        context = (
            f"close={close_now:.2f} lower={lower_now:.2f} upper={upper_now:.2f} "
            f"mean={mean_now:.2f} z={z_score:.3f}"
        )

        # BUY: 하단 터치 후 회복 (close가 lower_band 아래였다가 위로 복귀)
        if close_now < lower_now and close_now > lower_prev:
            confidence = Confidence.HIGH if abs(z_score) > _HIGH_CONF_Z else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"하단밴드 터치 후 회복: close({close_now:.2f})<lower({lower_now:.2f}) "
                    f"AND close>lower_prev({lower_prev:.2f}), z={z_score:.3f}"
                ),
                invalidation=f"close < lower_band ({lower_now:.2f}) 지속",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 상단 터치 후 하락 (close가 upper_band 위였다가 아래로 복귀)
        if close_now > upper_now and close_now < upper_prev:
            confidence = Confidence.HIGH if abs(z_score) > _HIGH_CONF_Z else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"상단밴드 터치 후 하락: close({close_now:.2f})>upper({upper_now:.2f}) "
                    f"AND close<upper_prev({upper_prev:.2f}), z={z_score:.3f}"
                ),
                invalidation=f"close > upper_band ({upper_now:.2f}) 지속",
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
