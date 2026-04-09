"""
PriceActionMomentumStrategy: 가격 행동 기반 모멘텀 전략.

- Momentum Score (0~5):
    +1 close > ema50
    +1 close > 20봉 전 close (중기 모멘텀)
    +1 close > 5봉 전 close  (단기 모멘텀)
    +1 현재 봉 양봉
    +1 볼륨 > 20봉 평균
- BUY:  bull_score >= 4
- SELL: bear_score >= 4  (close < ema50, close < 20봉 전, close < 5봉 전, 음봉, 볼륨 급증)
- confidence: HIGH if score == 5, MEDIUM otherwise
- 최소 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_BUY_THRESHOLD = 4
_SELL_THRESHOLD = 4


class PriceActionMomentumStrategy(BaseStrategy):
    name = "price_action_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])
        close_20ago = float(df["close"].iloc[idx - 20])
        close_5ago = float(df["close"].iloc[idx - 5])
        is_bullish = close > float(df["open"].iloc[idx])
        vol = float(df["volume"].iloc[idx])
        avg_vol = float(df["volume"].iloc[idx - 20:idx].mean())
        vol_surge = vol > avg_vol

        bull_score = sum([
            close > ema50,
            close > close_20ago,
            close > close_5ago,
            is_bullish,
            vol_surge,
        ])
        bear_score = sum([
            close < ema50,
            close < close_20ago,
            close < close_5ago,
            not is_bullish,
            vol_surge,  # 볼륨 급증은 양방향 유효
        ])

        context = (
            f"close={close:.2f} ema50={ema50:.2f} "
            f"bull={bull_score} bear={bear_score} vol_surge={vol_surge}"
        )

        if bull_score >= _BUY_THRESHOLD:
            confidence = Confidence.HIGH if bull_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"PA Momentum BUY: bull_score={bull_score}/5",
                invalidation=f"bull_score<{_BUY_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        if bear_score >= _SELL_THRESHOLD:
            confidence = Confidence.HIGH if bear_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"PA Momentum SELL: bear_score={bear_score}/5",
                invalidation=f"bear_score<{_SELL_THRESHOLD}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: bull={bull_score} bear={bear_score}",
            context,
            context,
        )

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
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
