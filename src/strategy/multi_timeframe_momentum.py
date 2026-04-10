"""
MultiTimeframeMomentumStrategy:
- 단기/중기/장기 모멘텀 일관성 + 거래량 확인
- BUY:  bull_score >= 3 AND vol_confirm
- SELL: bear_score >= 3 AND vol_confirm
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class MultiTimeframeMomentumStrategy(BaseStrategy):
    name = "multi_timeframe_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        volume = df["volume"]

        mom_short = close.pct_change(5)
        mom_mid = close.pct_change(10)
        mom_long = close.pct_change(20)

        vol_mean = volume.rolling(10, min_periods=1).mean()

        idx = len(df) - 2
        ms = mom_short.iloc[idx]
        mm = mom_mid.iloc[idx]
        ml = mom_long.iloc[idx]
        vol_val = volume.iloc[idx]
        vol_mean_val = vol_mean.iloc[idx]

        # NaN 체크
        if any(pd.isna(x) for x in [ms, mm, ml, vol_val, vol_mean_val]):
            return self._hold(df, "NaN in indicators")

        bull_score = int(ms > 0) + int(mm > 0) + int(ml > 0)
        bear_score = int(ms < 0) + int(mm < 0) + int(ml < 0)
        vol_confirm = vol_val > vol_mean_val

        last = self._last(df)
        entry = float(last["close"])
        context = (
            f"mom_short={ms:.4f} mom_mid={mm:.4f} mom_long={ml:.4f} "
            f"bull={bull_score} bear={bear_score} vol_confirm={vol_confirm}"
        )

        def _confidence() -> Confidence:
            all_aligned = (bull_score == 3 or bear_score == 3)
            ms_mean = mom_short.rolling(20, min_periods=1).mean().iloc[idx]
            if pd.isna(ms_mean):
                return Confidence.MEDIUM
            if all_aligned and abs(ms) > abs(ms_mean):
                return Confidence.HIGH
            return Confidence.MEDIUM

        if bull_score >= 3 and vol_confirm:
            return Signal(
                action=Action.BUY,
                confidence=_confidence(),
                strategy=self.name,
                entry_price=entry,
                reasoning=f"멀티타임프레임 모멘텀 상승 일치 (bull_score=3, vol_confirm)",
                invalidation="bull_score < 3 or volume below 10-bar mean",
                bull_case=context,
                bear_case=context,
            )

        if bear_score >= 3 and vol_confirm:
            return Signal(
                action=Action.SELL,
                confidence=_confidence(),
                strategy=self.name,
                entry_price=entry,
                reasoning=f"멀티타임프레임 모멘텀 하락 일치 (bear_score=3, vol_confirm)",
                invalidation="bear_score < 3 or volume below 10-bar mean",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No consensus: bull={bull_score} bear={bear_score} vol={vol_confirm}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2
        entry = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
