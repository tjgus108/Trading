"""
ADL (Accumulation/Distribution Line) 전략:
- CLV = ((close - low) - (high - close)) / (high - low + 1e-10)
- MFV = CLV * volume
- ADL = cumsum(MFV)
- ADL_EMA = EMA(ADL, 14)
- BUY: ADL 상향 크로스 AND close > ema50
- SELL: ADL 하향 크로스 AND close < ema50
- Confidence: HIGH if 2봉 연속 같은 방향, MEDIUM otherwise
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_ADL_EMA_SPAN = 14


class ADLStrategy(BaseStrategy):
    name = "adl"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        clv = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / (df["high"] - df["low"] + 1e-10)
        mfv = clv * df["volume"]
        adl = mfv.cumsum()
        adl_ema = adl.ewm(span=_ADL_EMA_SPAN, adjust=False).mean()

        adl_now = float(adl.iloc[idx])
        adl_prev = float(adl.iloc[idx - 1])
        ema_now = float(adl_ema.iloc[idx])
        ema_prev = float(adl_ema.iloc[idx - 1])
        adl_prev2 = float(adl.iloc[idx - 2])
        ema_prev2 = float(adl_ema.iloc[idx - 2])

        cross_up = adl_prev <= ema_prev and adl_now > ema_now
        cross_down = adl_prev >= ema_prev and adl_now < ema_now

        close_now = float(df["close"].iloc[idx])
        ema50_now = float(df["ema50"].iloc[idx])

        if cross_up and close_now > ema50_now:
            conf = Confidence.HIGH if adl_prev2 > ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"ADL 상향 크로스: ADL={adl_now:.2f} > ADL_EMA={ema_now:.2f}, close={close_now:.2f} > ema50={ema50_now:.2f}",
                invalidation="ADL < ADL_EMA 또는 close < ema50",
                bull_case="ADL 매집 신호, 볼륨 강세",
                bear_case="단기 크로스일 수 있음",
            )

        if cross_down and close_now < ema50_now:
            conf = Confidence.HIGH if adl_prev2 < ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"ADL 하향 크로스: ADL={adl_now:.2f} < ADL_EMA={ema_now:.2f}, close={close_now:.2f} < ema50={ema50_now:.2f}",
                invalidation="ADL > ADL_EMA 또는 close > ema50",
                bull_case="단기 반등일 수 있음",
                bear_case="ADL 분배 신호, 볼륨 약세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_now,
            reasoning=f"ADL 크로스 없음: ADL={adl_now:.2f}, ADL_EMA={ema_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
