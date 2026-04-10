"""
WedgePatternStrategy: Rising/Falling Wedge 패턴 감지.

- 최근 20봉 high/low의 선형 회귀로 수렴 채널 감지
- Rising wedge: high_slope > 0 AND low_slope > 0 AND low_slope > high_slope
- Falling wedge: high_slope < 0 AND low_slope < 0 AND high_slope < low_slope
- BUY: Falling wedge + close > recent 5봉 최고가 (돌파)
- SELL: Rising wedge + close < recent 5봉 최저가
- confidence: |high_slope - low_slope| > 0.5 → HIGH
- 최소 행: 25
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
LOOKBACK = 20
BREAKOUT_BARS = 5
HIGH_CONF_THRESHOLD = 0.5


class WedgePatternStrategy(BaseStrategy):
    name = "wedge_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
            )

        last = self._last(df)
        close = float(last["close"])

        highs = df["high"].iloc[-LOOKBACK - 1 : -1].values
        lows = df["low"].iloc[-LOOKBACK - 1 : -1].values
        x = np.arange(len(highs))

        high_slope = float(np.polyfit(x, highs, 1)[0])
        low_slope = float(np.polyfit(x, lows, 1)[0])

        convergence = abs(high_slope - low_slope)
        confidence = Confidence.HIGH if convergence > HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        # 최근 5봉 (현재 진행봉 제외)
        recent5_high = float(df["high"].iloc[-BREAKOUT_BARS - 1 : -1].max())
        recent5_low = float(df["low"].iloc[-BREAKOUT_BARS - 1 : -1].min())

        rising_wedge = (
            high_slope > 0
            and low_slope > 0
            and low_slope > high_slope
        )
        falling_wedge = (
            high_slope < 0
            and low_slope < 0
            and high_slope < low_slope
        )

        if falling_wedge and close > recent5_high:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Falling wedge 돌파: high_slope={high_slope:.4f}, low_slope={low_slope:.4f}, "
                    f"close={close:.4f} > 5봉 최고가={recent5_high:.4f}, "
                    f"수렴각={convergence:.4f}"
                ),
                invalidation=f"Close below {recent5_low:.4f}",
                bull_case=f"Falling wedge 수렴 후 상단 돌파. convergence={convergence:.4f}",
                bear_case=f"거짓 돌파 가능성. high_slope={high_slope:.4f}",
            )

        if rising_wedge and close < recent5_low:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Rising wedge 이탈: high_slope={high_slope:.4f}, low_slope={low_slope:.4f}, "
                    f"close={close:.4f} < 5봉 최저가={recent5_low:.4f}, "
                    f"수렴각={convergence:.4f}"
                ),
                invalidation=f"Close above {recent5_high:.4f}",
                bull_case=f"거짓 이탈 가능성. low_slope={low_slope:.4f}",
                bear_case=f"Rising wedge 수렴 후 하단 이탈. convergence={convergence:.4f}",
            )

        pattern = "rising_wedge" if rising_wedge else ("falling_wedge" if falling_wedge else "none")
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"패턴={pattern}, high_slope={high_slope:.4f}, low_slope={low_slope:.4f}, "
                f"돌파 조건 미충족"
            ),
            invalidation="",
            bull_case=f"Falling wedge 형성 중" if falling_wedge else "",
            bear_case=f"Rising wedge 형성 중" if rising_wedge else "",
        )
