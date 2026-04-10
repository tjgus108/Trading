"""
Chande Momentum Strategy.
- CMO = 100 * (up_sum - down_sum) / (up_sum + down_sum)
- cmo_ma = CMO.rolling(9).mean() (시그널)

BUY:  cmo crosses above cmo_ma AND cmo < 0 (과매도 구간)
SELL: cmo crosses below cmo_ma AND cmo > 0 (과매수 구간)
HOLD: 그 외

confidence: HIGH if abs(cmo) > 50 else MEDIUM
최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 14
_MA_PERIOD = 9
_MIN_ROWS = 30


class ChandeMomentumStrategy(BaseStrategy):
    name = "chande_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data for ChandeMomentum (need {_MIN_ROWS} rows)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        diff = df["close"].diff()
        up_sum = diff.clip(lower=0).rolling(_PERIOD).sum()
        down_sum = (-diff.clip(upper=0)).rolling(_PERIOD).sum()

        denom = up_sum + down_sum
        cmo = 100 * (up_sum - down_sum) / denom.where(denom != 0, other=1e-10)
        cmo_ma = cmo.rolling(_MA_PERIOD).mean()

        cmo_now = float(cmo.iloc[idx])
        cmo_prev = float(cmo.iloc[idx - 1])
        ma_now = float(cmo_ma.iloc[idx])
        ma_prev = float(cmo_ma.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        if any(pd.isna(v) for v in [cmo_now, cmo_prev, ma_now, ma_prev]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in CMO indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        # BUY: cmo crosses above cmo_ma AND cmo < 0
        if cmo_prev < ma_prev and cmo_now >= ma_now and cmo_now < 0:
            conf = Confidence.HIGH if abs(cmo_now) > 50 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ChandeMomentum BUY: CMO crossed above signal in oversold zone "
                    f"(cmo={cmo_now:.2f}, ma={ma_now:.2f})"
                ),
                invalidation="CMO falls back below signal line",
                bull_case=f"CMO {cmo_now:.2f} crossing up in oversold territory",
                bear_case="Possible false crossover",
            )

        # SELL: cmo crosses below cmo_ma AND cmo > 0
        if cmo_prev > ma_prev and cmo_now <= ma_now and cmo_now > 0:
            conf = Confidence.HIGH if abs(cmo_now) > 50 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"ChandeMomentum SELL: CMO crossed below signal in overbought zone "
                    f"(cmo={cmo_now:.2f}, ma={ma_now:.2f})"
                ),
                invalidation="CMO rises back above signal line",
                bull_case="Possible false crossover",
                bear_case=f"CMO {cmo_now:.2f} crossing down in overbought territory",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"ChandeMomentum HOLD: cmo={cmo_now:.2f}, ma={ma_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
