"""
PMO (Price Momentum Oscillator) 전략:
- ROC1 = ((close / close.shift(1)) - 1) * 100
- Smoothed1 = EMA(ROC1, 35) * 20
- PMO = EMA(Smoothed1, 20)
- Signal = EMA(PMO, 10)
- BUY: PMO 상향 크로스 Signal (이전 PMO <= 이전 Signal, 현재 PMO > Signal)
- SELL: PMO 하향 크로스 Signal
- confidence: HIGH if PMO > 2 (BUY) or PMO < -2 (SELL), MEDIUM otherwise
- 최소 60행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 60
_HIGH_CONF_THRESHOLD = 2.0


class PMOStrategy(BaseStrategy):
    name = "pmo"

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

        roc1 = (df["close"] / df["close"].shift(1) - 1) * 100
        smoothed1 = roc1.ewm(span=35, adjust=False).mean() * 20
        pmo = smoothed1.ewm(span=20, adjust=False).mean()
        signal = pmo.ewm(span=10, adjust=False).mean()

        pmo_now = float(pmo.iloc[idx])
        pmo_prev = float(pmo.iloc[idx - 1])
        sig_now = float(signal.iloc[idx])
        sig_prev = float(signal.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])

        # BUY: PMO 상향 크로스 Signal
        if pmo_prev <= sig_prev and pmo_now > sig_now:
            conf = Confidence.HIGH if pmo_now > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PMO 상향 크로스: PMO {pmo_prev:.4f} → {pmo_now:.4f}, Signal {sig_now:.4f}",
                invalidation="PMO가 Signal 아래로 재하락 시",
                bull_case=f"PMO {pmo_now:.4f} 상향 크로스, 상승 모멘텀 확인",
                bear_case="모멘텀 약화 시 되돌림 가능",
            )

        # SELL: PMO 하향 크로스 Signal
        if pmo_prev >= sig_prev and pmo_now < sig_now:
            conf = Confidence.HIGH if pmo_now < -_HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PMO 하향 크로스: PMO {pmo_prev:.4f} → {pmo_now:.4f}, Signal {sig_now:.4f}",
                invalidation="PMO가 Signal 위로 재상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"PMO {pmo_now:.4f} 하향 크로스, 하락 모멘텀 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"PMO 중립: PMO {pmo_now:.4f}, Signal {sig_now:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
