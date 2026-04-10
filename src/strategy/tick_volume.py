"""
TickVolumeStrategy:
- volume을 틱 대리로 사용하여 매수/매도 압력 분석
- BUY: cum_delta > cum_delta_ma AND cum_delta > 0 AND volume > tick_vol_ma
- SELL: cum_delta < cum_delta_ma AND cum_delta < 0 AND volume > tick_vol_ma
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class TickVolumeStrategy(BaseStrategy):
    name = "tick_volume"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for tick_volume",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        close = df["close"]
        volume = df["volume"]

        tick_vol_ma = volume.rolling(20, min_periods=1).mean()
        price_change = close.diff()
        up_vol = volume * (price_change > 0)
        down_vol = volume * (price_change < 0)
        cum_delta = (up_vol - down_vol).rolling(10, min_periods=1).sum()
        cum_delta_ma = cum_delta.rolling(5, min_periods=1).mean()

        cd = float(cum_delta.iloc[idx])
        cd_ma = float(cum_delta_ma.iloc[idx])
        vol_now = float(volume.iloc[idx])
        tvm = float(tick_vol_ma.iloc[idx])
        entry = float(close.iloc[idx])

        if any(pd.isna(v) for v in [cd, cd_ma, vol_now, tvm]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in tick_volume indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        vol_active = vol_now > tvm
        conf = Confidence.HIGH if vol_now > tvm * 1.5 else Confidence.MEDIUM

        if cd > cd_ma and cd > 0 and vol_active:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"tick_volume BUY: cum_delta={cd:.2f} > ma={cd_ma:.2f}, "
                    f"vol={vol_now:.2f} > tick_vol_ma={tvm:.2f}"
                ),
                invalidation="cum_delta가 ma 아래로 하락 또는 음수 전환",
                bull_case="매수 틱 볼륨 우세, 상승 압력 확인",
                bear_case="단기 수급 쏠림일 수 있음",
            )

        if cd < cd_ma and cd < 0 and vol_active:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"tick_volume SELL: cum_delta={cd:.2f} < ma={cd_ma:.2f}, "
                    f"vol={vol_now:.2f} > tick_vol_ma={tvm:.2f}"
                ),
                invalidation="cum_delta가 ma 위로 회복 또는 양수 전환",
                bull_case="단기 반등 가능",
                bear_case="매도 틱 볼륨 우세, 하락 압력 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"tick_volume HOLD: cum_delta={cd:.2f}, ma={cd_ma:.2f}, "
                f"vol={vol_now:.2f}, tick_vol_ma={tvm:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
