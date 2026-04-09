"""
RVI (Relative Vigor Index) 전략:
- Value = (close - open) / (high - low + 1e-10)
- Numerator = (Value + 2*Value.shift(1) + 2*Value.shift(2) + Value.shift(3)) / 6
- Denominator = ((high-low) + 2*(high.shift(1)-low.shift(1)) + 2*(high.shift(2)-low.shift(2)) + (high.shift(3)-low.shift(3))) / 6
- RVI = Numerator.rolling(10).sum() / Denominator.rolling(10).sum()
- Signal = (RVI + 2*RVI.shift(1) + 2*RVI.shift(2) + RVI.shift(3)) / 6
- BUY: RVI 상향 크로스 Signal
- SELL: RVI 하향 크로스 Signal
- confidence: HIGH if |RVI| > 0.3, MEDIUM otherwise
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_HIGH_CONF_THRESHOLD = 0.3


class RVIStrategy(BaseStrategy):
    name = "rvi"

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

        close = df["close"]
        open_ = df["open"]
        high = df["high"]
        low = df["low"]

        value = (close - open_) / (high - low + 1e-10)

        numerator = (
            value
            + 2 * value.shift(1)
            + 2 * value.shift(2)
            + value.shift(3)
        ) / 6

        denominator = (
            (high - low)
            + 2 * (high.shift(1) - low.shift(1))
            + 2 * (high.shift(2) - low.shift(2))
            + (high.shift(3) - low.shift(3))
        ) / 6

        denom_safe = denominator.replace(0, float("nan"))
        rvi = numerator.rolling(10).sum() / denom_safe.rolling(10).sum()

        signal = (
            rvi
            + 2 * rvi.shift(1)
            + 2 * rvi.shift(2)
            + rvi.shift(3)
        ) / 6

        rvi_now = float(rvi.iloc[idx])
        rvi_prev = float(rvi.iloc[idx - 1])
        sig_now = float(signal.iloc[idx])
        sig_prev = float(signal.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])

        # NaN 체크
        import math
        if any(math.isnan(v) for v in [rvi_now, rvi_prev, sig_now, sig_prev]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="RVI 계산 불가 (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        # BUY: RVI 상향 크로스 Signal
        if rvi_prev <= sig_prev and rvi_now > sig_now:
            conf = Confidence.HIGH if abs(rvi_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"RVI 상향 크로스: RVI {rvi_prev:.4f} → {rvi_now:.4f}, Signal {sig_now:.4f}",
                invalidation="RVI가 Signal 아래로 재하락 시",
                bull_case=f"RVI {rvi_now:.4f} 상향 크로스, 상승 추세 확인",
                bear_case="모멘텀 약화 시 되돌림 가능",
            )

        # SELL: RVI 하향 크로스 Signal
        if rvi_prev >= sig_prev and rvi_now < sig_now:
            conf = Confidence.HIGH if abs(rvi_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"RVI 하향 크로스: RVI {rvi_prev:.4f} → {rvi_now:.4f}, Signal {sig_now:.4f}",
                invalidation="RVI가 Signal 위로 재상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"RVI {rvi_now:.4f} 하향 크로스, 하락 추세 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"RVI 중립: RVI {rvi_now:.4f}, Signal {sig_now:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
