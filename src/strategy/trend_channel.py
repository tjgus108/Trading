"""
Trend Channel Strategy: 선형 회귀 채널 기반 전략.

- 선형 회귀선: np.polyfit으로 기울기/절편 계산 (기간=20)
- Upper Channel = 회귀선 + 2 * std
- Lower Channel = 회귀선 - 2 * std
- BUY: close < Lower Channel AND slope > 0 (상승 추세)
- SELL: close > Upper Channel AND slope < 0 (하락 추세)
- confidence: HIGH if |채널 이탈| > std, MEDIUM otherwise
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendChannelStrategy(BaseStrategy):
    name = "trend_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return self._hold(df, "데이터 부족")

        idx = len(df) - 2
        period = 20

        y = df["close"].iloc[idx - period + 1: idx + 1].values
        x = np.arange(period)
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        fitted = np.polyval(coeffs, x)
        residuals = y - fitted
        std = float(np.std(residuals))
        current_fit = float(np.polyval(coeffs, period - 1))
        upper = current_fit + 2 * std
        lower = current_fit - 2 * std
        close = float(df["close"].iloc[idx])

        entry = close

        bull_case = (
            f"Price ({close:.2f}) near Lower Channel ({lower:.2f}). "
            f"Slope={slope:.4f}, Fit={current_fit:.2f}, Std={std:.2f}"
        )
        bear_case = (
            f"Price ({close:.2f}) near Upper Channel ({upper:.2f}). "
            f"Slope={slope:.4f}, Fit={current_fit:.2f}, Std={std:.2f}"
        )

        # BUY: 채널 하단 이탈 + 상승 추세
        if close < lower and slope > 0:
            deviation = lower - close
            conf = Confidence.HIGH if deviation > std else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Price below lower channel ({lower:.2f}), slope={slope:.4f} (uptrend). "
                    f"Deviation={deviation:.2f}, Std={std:.2f}."
                ),
                invalidation=f"Price falls further below lower channel or slope turns negative",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 채널 상단 이탈 + 하락 추세
        if close > upper and slope < 0:
            deviation = close - upper
            conf = Confidence.HIGH if deviation > std else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Price above upper channel ({upper:.2f}), slope={slope:.4f} (downtrend). "
                    f"Deviation={deviation:.2f}, Std={std:.2f}."
                ),
                invalidation=f"Price pulls back inside upper channel or slope turns positive",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"No channel breakout. Upper={upper:.2f}, Lower={lower:.2f}, Slope={slope:.4f}.",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
