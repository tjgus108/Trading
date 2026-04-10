"""
VolumeWeightedMomentum 전략: 거래량 가중 모멘텀 기반 추세 추종.
vw_momentum = (returns * vol_norm).rolling(10).sum()
vw_mom_ma = vw_momentum.rolling(5).mean()
BUY: vw_momentum > vw_mom_ma AND vw_momentum > 0
SELL: vw_momentum < vw_mom_ma AND vw_momentum < 0
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VolumeWeightedMomentumStrategy(BaseStrategy):
    name = "volume_weighted_momentum"

    _MIN_ROWS = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"Not enough data: {len(df)} < {self._MIN_ROWS}",
                invalidation="",
            )

        close = df["close"]
        volume = df["volume"]
        idx = len(df) - 2

        returns = close.pct_change()
        vol_norm = volume / (volume.rolling(20, min_periods=1).mean() + 1e-10)
        vw_momentum = (returns * vol_norm).rolling(10, min_periods=1).sum()
        vw_mom_ma = vw_momentum.rolling(5, min_periods=1).mean()
        vw_mom_std = vw_momentum.rolling(20, min_periods=1).std()

        entry = float(close.iloc[idx])
        vw_mom_val = float(vw_momentum.iloc[idx])
        vw_mom_ma_val = float(vw_mom_ma.iloc[idx])
        vw_mom_std_val = float(vw_mom_std.iloc[idx]) if not pd.isna(vw_mom_std.iloc[idx]) else 0.0

        # NaN 체크
        if any(pd.isna(v) for v in [entry, vw_mom_val, vw_mom_ma_val]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry if not pd.isna(entry) else 0.0,
                reasoning="NaN in indicators",
                invalidation="",
            )

        high_conf = (
            abs(vw_mom_val) > vw_mom_std_val
            if vw_mom_std_val > 0
            else False
        )

        bull_case = (
            f"vw_momentum={vw_mom_val:.6f}, vw_mom_ma={vw_mom_ma_val:.6f}, "
            f"std={vw_mom_std_val:.6f}"
        )
        bear_case = bull_case

        if vw_mom_val > vw_mom_ma_val and vw_mom_val > 0:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VW momentum positive and above MA. "
                    f"vw_mom={vw_mom_val:.6f} > ma={vw_mom_ma_val:.6f}."
                ),
                invalidation=f"vw_momentum drops below 0 or below MA",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if vw_mom_val < vw_mom_ma_val and vw_mom_val < 0:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VW momentum negative and below MA. "
                    f"vw_mom={vw_mom_val:.6f} < ma={vw_mom_ma_val:.6f}."
                ),
                invalidation=f"vw_momentum rises above 0 or above MA",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No clear VW momentum signal. "
                f"vw_mom={vw_mom_val:.6f}, ma={vw_mom_ma_val:.6f}."
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
