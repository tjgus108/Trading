"""
OBV (On-Balance Volume) 전략:
- OBV: 종가 상승 +volume, 하락 -volume, 동일 0 누적
- OBV_EMA: OBV의 20기간 EMA (시그널)
- BUY: OBV가 OBV_EMA를 상향 돌파 AND close > ema50
- SELL: OBV가 OBV_EMA를 하향 돌파 AND close < ema50
- Confidence: HIGH if 2봉 전에도 같은 방향, MEDIUM if 방금 크로스
- 최소 30행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_OBV_EMA_SPAN = 20


class OBVStrategy(BaseStrategy):
    name = "obv"

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

        # OBV 계산
        close_diff = df["close"].diff()
        obv = (df["volume"] * close_diff.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))).cumsum()
        obv_ema = obv.ewm(span=_OBV_EMA_SPAN, adjust=False).mean()

        obv_now = float(obv.iloc[idx])
        obv_prev = float(obv.iloc[idx - 1])
        ema_now = float(obv_ema.iloc[idx])
        ema_prev = float(obv_ema.iloc[idx - 1])
        obv_prev2 = float(obv.iloc[idx - 2])
        ema_prev2 = float(obv_ema.iloc[idx - 2])

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        cross_up = obv_prev <= ema_prev and obv_now > ema_now
        cross_down = obv_prev >= ema_prev and obv_now < ema_now

        last = self._last(df)

        if cross_up and close > ema50:
            conf = Confidence.HIGH if obv_prev2 > ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"OBV 상향 돌파: OBV={obv_now:.0f} > OBV_EMA={ema_now:.0f}, close={close:.2f} > ema50={ema50:.2f}",
                invalidation=f"OBV < OBV_EMA 또는 close < ema50",
                bull_case=f"OBV 상승 추세 전환, 볼륨 강세",
                bear_case="단기 크로스일 수 있음",
            )

        if cross_down and close < ema50:
            conf = Confidence.HIGH if obv_prev2 < ema_prev2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"OBV 하향 돌파: OBV={obv_now:.0f} < OBV_EMA={ema_now:.0f}, close={close:.2f} < ema50={ema50:.2f}",
                invalidation=f"OBV > OBV_EMA 또는 close > ema50",
                bull_case="단기 반등일 수 있음",
                bear_case=f"OBV 하락 추세 전환, 볼륨 약세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"OBV 크로스 없음: OBV={obv_now:.0f}, OBV_EMA={ema_now:.0f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
