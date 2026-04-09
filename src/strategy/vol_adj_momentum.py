"""
VolatilityAdjustedMomentum 전략: 변동성으로 정규화된 모멘텀 신호.

- raw_momentum  = close / close.shift(14) - 1
- hist_vol       = close.pct_change().rolling(14).std()
- vol_adj_mom    = raw_momentum / (hist_vol + 1e-10)
- signal_line    = EWM(vol_adj_mom, span=9)
- BUY:  vol_adj_mom > signal_line AND vol_adj_mom > 0
- SELL: vol_adj_mom < signal_line AND vol_adj_mom < 0
- confidence: HIGH if |vol_adj_mom| > 2.0, MEDIUM if > 0
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VolAdjMomentumStrategy(BaseStrategy):
    name = "vol_adj_momentum"

    def __init__(self, mom_period: int = 14, signal_span: int = 9):
        self.mom_period = mom_period
        self.signal_span = signal_span

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        close = df["close"]

        raw_momentum = close / close.shift(self.mom_period) - 1
        hist_vol = close.pct_change().rolling(self.mom_period).std()
        vol_adj_mom = raw_momentum / (hist_vol + 1e-10)
        signal_line = vol_adj_mom.ewm(span=self.signal_span, adjust=False).mean()

        result = df.copy()
        result["_vol_adj_mom"] = vol_adj_mom
        result["_signal_line"] = signal_line
        return result

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < 25",
                invalidation="",
            )

        computed = self._compute(df)

        # 마지막 완성 캔들 = iloc[-2]
        vam = float(computed["_vol_adj_mom"].iloc[-2])
        sig = float(computed["_signal_line"].iloc[-2])
        entry = float(df["close"].iloc[-2])

        # NaN 방어
        if pd.isna(vam) or pd.isna(sig):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 계산 중 NaN 발생.",
                invalidation="",
            )

        abs_vam = abs(vam)
        if abs_vam > 2.0:
            conf = Confidence.HIGH
        elif abs_vam > 0:
            conf = Confidence.MEDIUM
        else:
            conf = Confidence.LOW

        # BUY 조건
        if vam > sig and vam > 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VolAdjMom={vam:.3f} > Signal={sig:.3f}, 양수 모멘텀."
                ),
                invalidation="vol_adj_mom이 signal_line 하회 또는 음전 시 무효.",
                bull_case="변동성 대비 강한 상승 모멘텀 확인.",
                bear_case="모멘텀 약화 가능성 존재.",
            )

        # SELL 조건
        if vam < sig and vam < 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"VolAdjMom={vam:.3f} < Signal={sig:.3f}, 음수 모멘텀."
                ),
                invalidation="vol_adj_mom이 signal_line 상회 또는 양전 시 무효.",
                bull_case="모멘텀 회복 가능성 존재.",
                bear_case="변동성 대비 강한 하락 모멘텀 확인.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"VolAdjMom={vam:.3f}, Signal={sig:.3f}. 조건 미충족.",
            invalidation="",
        )
