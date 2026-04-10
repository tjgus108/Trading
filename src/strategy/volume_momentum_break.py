"""
VolumeMomentumBreakStrategy:
- BUY:  거래량 급증(>2x 평균) + ROC3 > ROC3_MA AND ROC3 > 0  (상승 모멘텀 가속)
- SELL: 거래량 급증(>2x 평균) + ROC3 < ROC3_MA AND ROC3 < 0  (하락 모멘텀 가속)
- confidence: HIGH if vol_ratio > 3.0 else MEDIUM
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class VolumeMomentumBreakStrategy(BaseStrategy):
    name = "volume_momentum_break"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "데이터 부족")

        close = df["close"]
        volume = df["volume"]

        vol_ma = volume.rolling(20, min_periods=1).mean()
        vol_ratio = volume / (vol_ma + 1e-10)
        roc3 = close.pct_change(3)
        roc3_ma = roc3.rolling(10, min_periods=1).mean()
        vol_surge = vol_ratio > 2.0

        idx = len(df) - 2

        # NaN 체크
        if pd.isna(vol_ratio.iloc[idx]) or pd.isna(roc3.iloc[idx]) or pd.isna(roc3_ma.iloc[idx]):
            return self._hold(df, "NaN 데이터")

        last_vol_surge = bool(vol_surge.iloc[idx])
        last_roc3 = float(roc3.iloc[idx])
        last_roc3_ma = float(roc3_ma.iloc[idx])
        last_vol_ratio = float(vol_ratio.iloc[idx])
        last_close = float(close.iloc[idx])

        confidence = Confidence.HIGH if last_vol_ratio > 3.0 else Confidence.MEDIUM
        info = f"vol_ratio={last_vol_ratio:.2f} roc3={last_roc3:.4f} roc3_ma={last_roc3_ma:.4f} close={last_close:.4f}"

        if last_vol_surge and last_roc3 > last_roc3_ma and last_roc3 > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"거래량 급증 + 상승 모멘텀 가속: {info}",
                invalidation="vol_ratio < 2.0 또는 roc3 < 0",
                bull_case=info,
                bear_case=info,
            )

        if last_vol_surge and last_roc3 < last_roc3_ma and last_roc3 < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"거래량 급증 + 하락 모멘텀 가속: {info}",
                invalidation="vol_ratio < 2.0 또는 roc3 > 0",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"조건 미충족: {info}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
