"""
PriceOscillatorStrategy (APO):
- BUY: apo_hist crosses above 0 AND apo < 0
- SELL: apo_hist crosses below 0 AND apo > 0
- Confidence: HIGH if |apo| > close.rolling(20).std() * 0.1, else MEDIUM
- 최소 30행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class PriceOscillatorStrategy(BaseStrategy):
    name = "price_oscillator"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for PriceOscillator (need 30 rows)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = df["close"]
        ema10 = close.ewm(span=10, adjust=False).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()
        apo = ema10 - ema20
        apo_signal = apo.ewm(span=9, adjust=False).mean()
        apo_hist = apo - apo_signal

        idx = len(df) - 2
        apo_now = float(apo.iloc[idx])
        apo_prev = float(apo.iloc[idx - 1])
        hist_now = float(apo_hist.iloc[idx])
        hist_prev = float(apo_hist.iloc[idx - 1])

        if any(pd.isna(v) for v in [apo_now, apo_prev, hist_now, hist_prev]):
            entry = float(close.iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="PriceOscillator: NaN 값 존재",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close_std = float(close.rolling(20).std().iloc[idx])
        conf = Confidence.HIGH if abs(apo_now) > close_std * 0.1 else Confidence.MEDIUM
        entry = float(close.iloc[idx])

        # BUY: apo_hist crosses above 0 AND apo < 0
        if hist_prev <= 0 and hist_now > 0 and apo_now < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"APO 히스토그램 상향 전환 (음수 구간): hist {hist_prev:.4f} → {hist_now:.4f}, "
                    f"APO={apo_now:.4f}"
                ),
                invalidation="APO 히스토그램이 다시 0 하향 크로스 시",
                bull_case=f"APO {apo_now:.4f} < 0 구간에서 상승 전환, 매수 기회",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: apo_hist crosses below 0 AND apo > 0
        if hist_prev >= 0 and hist_now < 0 and apo_now > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"APO 히스토그램 하향 전환 (양수 구간): hist {hist_prev:.4f} → {hist_now:.4f}, "
                    f"APO={apo_now:.4f}"
                ),
                invalidation="APO 히스토그램이 다시 0 상향 크로스 시",
                bull_case="단기 반등일 수 있음",
                bear_case=f"APO {apo_now:.4f} > 0 구간에서 하락 전환, 매도 기회",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"PriceOscillator 중립: APO={apo_now:.4f}, hist={hist_now:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
