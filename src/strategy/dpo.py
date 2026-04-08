"""
DPO (Detrended Price Oscillator) 전략:
- 추세 제거 후 단기 사이클 분석
- BUY: DPO < 0 AND 상승 중 (바닥에서 반등)
- SELL: DPO > 0 AND 하락 중 (고점에서 반락)
- Confidence: HIGH if |DPO| > 3.0, MEDIUM otherwise
- 최소 30행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 30
_HIGH_CONF_THRESHOLD = 3.0
_BUY_FILTER = -2.0
_SELL_FILTER = 2.0


class DPOStrategy(BaseStrategy):
    name = "dpo"

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
        period = _PERIOD
        shift = period // 2 + 1  # = 11

        ema20 = df["close"].ewm(span=period, adjust=False).mean()
        dpo = df["close"] - ema20.shift(shift)

        dpo_now = float(dpo.iloc[idx])
        dpo_prev = float(dpo.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        rising = dpo_now > dpo_prev
        falling = dpo_now < dpo_prev

        # BUY: DPO < 0 AND 상승 중 (바닥 반등)
        if dpo_now < 0 and rising:
            conf = Confidence.HIGH if abs(dpo_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            filter_note = " (강한 과매도 반등)" if dpo_now <= _BUY_FILTER else ""
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"DPO 사이클 바닥 반등: DPO {dpo_prev:.2f} → {dpo_now:.2f}{filter_note}",
                invalidation="DPO 재하락 시",
                bull_case=f"DPO {dpo_now:.2f}, 사이클 바닥에서 반등 중",
                bear_case="단기 반등에 그칠 수 있음",
            )

        # SELL: DPO > 0 AND 하락 중 (고점 반락)
        if dpo_now > 0 and falling:
            conf = Confidence.HIGH if abs(dpo_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            filter_note = " (강한 과매수 반락)" if dpo_now >= _SELL_FILTER else ""
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"DPO 사이클 고점 반락: DPO {dpo_prev:.2f} → {dpo_now:.2f}{filter_note}",
                invalidation="DPO 재상승 시",
                bull_case="단기 조정에 그칠 수 있음",
                bear_case=f"DPO {dpo_now:.2f}, 사이클 고점에서 하락 중",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"DPO 중립: {dpo_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
