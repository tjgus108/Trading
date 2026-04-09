"""
PriceMomentumOscillator (PMO) 전략:
- ROC_1 = close.pct_change() * 100
- Smoothed1 = ROC_1.ewm(span=35, adjust=False).mean() * 10
- PMO = Smoothed1.ewm(span=20, adjust=False).mean()
- Signal = PMO.ewm(span=10, adjust=False).mean()
- BUY: PMO crosses above Signal AND PMO < 0 (oversold)
- SELL: PMO crosses below Signal AND PMO > 0 (overbought)
- confidence: |PMO - Signal| > 0.5 → HIGH, 그 외 MEDIUM
- 최소 행: 60
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 60
_HIGH_CONF_DIFF = 0.5


class PriceMomentumOscillator(BaseStrategy):
    name = "pmo_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        roc1 = df["close"].pct_change() * 100
        smoothed1 = roc1.ewm(span=35, adjust=False).mean() * 10
        pmo = smoothed1.ewm(span=20, adjust=False).mean()
        signal_line = pmo.ewm(span=10, adjust=False).mean()

        pmo_now = float(pmo.iloc[idx])
        pmo_prev = float(pmo.iloc[idx - 1])
        sig_now = float(signal_line.iloc[idx])
        sig_prev = float(signal_line.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])
        diff = abs(pmo_now - sig_now)
        conf = Confidence.HIGH if diff > _HIGH_CONF_DIFF else Confidence.MEDIUM

        info = f"PMO={pmo_now:.4f} Signal={sig_now:.4f} diff={diff:.4f}"

        # BUY: crossover above signal AND PMO < 0 (oversold)
        if pmo_prev < sig_prev and pmo_now > sig_now and pmo_now < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PMO 상향 크로스 (oversold): {info}",
                invalidation="PMO가 Signal 아래로 재하락 시",
                bull_case=f"PMO oversold 구간 크로스오버: {info}",
                bear_case="모멘텀 약화 시 되돌림 가능",
            )

        # SELL: crossover below signal AND PMO > 0 (overbought)
        if pmo_prev > sig_prev and pmo_now < sig_now and pmo_now > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"PMO 하향 크로스 (overbought): {info}",
                invalidation="PMO가 Signal 위로 재상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"PMO overbought 구간 하향 크로스: {info}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"PMO 중립: {info}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
