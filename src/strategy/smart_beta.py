"""
SmartBetaStrategy:
- 저변동성 + 고모멘텀 스마트 베타 팩터
- composite_score = (1 - vol_rank)*0.5 + mom_rank*0.5
- BUY:  composite_score > 0.6 AND score > score_ma
- SELL: composite_score < 0.4 AND score < score_ma
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class SmartBetaStrategy(BaseStrategy):
    name = "smart_beta"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        realized_vol = close.pct_change().rolling(20, min_periods=1).std()
        vol_rank = realized_vol.rank(pct=True)

        momentum_12 = close.pct_change(12)
        mom_rank = momentum_12.rank(pct=True)

        composite_score = (1 - vol_rank) * 0.5 + mom_rank * 0.5
        score_ma = composite_score.rolling(5, min_periods=1).mean()

        idx = len(df) - 2
        cs = composite_score.iloc[idx]
        sma = score_ma.iloc[idx]

        if any(pd.isna(x) for x in [cs, sma]):
            return self._hold(df, "NaN in composite_score or score_ma")

        last = self._last(df)
        entry = float(last["close"])
        context = f"composite_score={cs:.4f} score_ma={sma:.4f}"

        def _confidence() -> Confidence:
            if cs > 0.75 or cs < 0.25:
                return Confidence.HIGH
            return Confidence.MEDIUM

        if cs > 0.6 and cs > sma:
            return Signal(
                action=Action.BUY,
                confidence=_confidence(),
                strategy=self.name,
                entry_price=entry,
                reasoning=f"스마트베타 매수: composite_score={cs:.4f}>0.6 and >score_ma({sma:.4f})",
                invalidation="composite_score <= 0.6 or score falls below score_ma",
                bull_case=context,
                bear_case=context,
            )

        if cs < 0.4 and cs < sma:
            return Signal(
                action=Action.SELL,
                confidence=_confidence(),
                strategy=self.name,
                entry_price=entry,
                reasoning=f"스마트베타 매도: composite_score={cs:.4f}<0.4 and <score_ma({sma:.4f})",
                invalidation="composite_score >= 0.4 or score rises above score_ma",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: composite_score={cs:.4f} score_ma={sma:.4f}", context, context)

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
