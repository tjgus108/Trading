"""
MomentumQualityV2Strategy: 모멘텀 품질 점수 (일관성 + 강도).

- roc5  = close.pct_change(5)
- roc10 = close.pct_change(10)
- roc20 = close.pct_change(20)
- consistency = (roc5>0) + (roc10>0) + (roc20>0)  → 0~3
- strength = roc5.rolling(5).mean()

- BUY:  consistency >= 3 AND strength > 0 AND roc5 > roc10
- SELL: consistency <= 0 AND strength < 0 AND roc5 < roc10
- confidence: HIGH if consistency==3 AND |strength| > strength.rolling(20).std() else MEDIUM
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class MomentumQualityV2Strategy(BaseStrategy):
    name = "momentum_quality_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        roc5_series = close.pct_change(5)
        roc10_series = close.pct_change(10)
        roc20_series = close.pct_change(20)

        consistency_series = (
            (roc5_series > 0).astype(int)
            + (roc10_series > 0).astype(int)
            + (roc20_series > 0).astype(int)
        )
        strength_series = roc5_series.rolling(5, min_periods=1).mean()
        strength_std_series = strength_series.rolling(20, min_periods=1).std()

        idx = len(df) - 2
        roc5 = float(roc5_series.iloc[idx])
        roc10 = float(roc10_series.iloc[idx])
        consistency = int(consistency_series.iloc[idx])
        strength = float(strength_series.iloc[idx])
        strength_std = float(strength_std_series.iloc[idx])
        entry_price = float(close.iloc[idx])

        if pd.isna(roc5) or pd.isna(roc10) or pd.isna(strength):
            return self._hold(df, "Indicator NaN")

        info = (
            f"consistency={consistency} strength={strength:.6f} "
            f"roc5={roc5:.6f} roc10={roc10:.6f} strength_std={strength_std:.6f}"
        )

        strength_std_safe = (
            strength_std
            if not pd.isna(strength_std) and strength_std > 0
            else None
        )

        if consistency >= 3 and strength > 0 and roc5 > roc10:
            confidence = (
                Confidence.HIGH
                if consistency == 3
                and strength_std_safe is not None
                and abs(strength) > strength_std_safe
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"모멘텀 품질 강세: {info}",
                invalidation="consistency 하락 또는 strength 음전환",
                bull_case=info,
                bear_case=info,
            )

        if consistency <= 0 and strength < 0 and roc5 < roc10:
            confidence = (
                Confidence.HIGH
                if consistency == 0
                and strength_std_safe is not None
                and abs(strength) > strength_std_safe
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"모멘텀 품질 약세: {info}",
                invalidation="consistency 상승 또는 strength 양전환",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
