"""
FractalBreakStrategy: Williams Fractal 기반 돌파 전략.
- 5봉 패턴으로 상단/하단 fractal 탐지
- BUY: close > last_up_fractal (상단 fractal 돌파)
- SELL: close < last_down_fractal (하단 fractal 붕괴)
- Confidence: HIGH if ATR14 > 0 and |close - fractal| / close > 0.01, else MEDIUM
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15


class FractalBreakStrategy(BaseStrategy):
    name = "fractal_break"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for fractal_break")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])

        atr14 = 0.0
        try:
            atr14 = float(last.get("atr14", 0.0))
        except Exception:
            atr14 = 0.0

        last_up: Optional[float] = None
        last_down: Optional[float] = None

        for i in range(idx - 2, max(1, idx - 20), -1):
            if i + 2 < len(df) and i - 2 >= 0:
                if (float(df['high'].iloc[i]) > float(df['high'].iloc[i - 2]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i - 1]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i + 1]) and
                        float(df['high'].iloc[i]) > float(df['high'].iloc[i + 2])):
                    last_up = float(df['high'].iloc[i])
                    break

        for i in range(idx - 2, max(1, idx - 20), -1):
            if i + 2 < len(df) and i - 2 >= 0:
                if (float(df['low'].iloc[i]) < float(df['low'].iloc[i - 2]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i - 1]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i + 1]) and
                        float(df['low'].iloc[i]) < float(df['low'].iloc[i + 2])):
                    last_down = float(df['low'].iloc[i])
                    break

        def _confidence(fractal_price: float) -> Confidence:
            if atr14 > 0 and abs(close - fractal_price) / close > 0.01:
                return Confidence.HIGH
            return Confidence.MEDIUM

        if last_up is not None and close > last_up:
            conf = _confidence(last_up)
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Fractal break up: close({close:.4f}) > up_fractal({last_up:.4f})",
                invalidation=f"Close below up fractal {last_up:.4f}",
                bull_case=f"Upper fractal breakout @ {last_up:.4f}",
                bear_case=f"Down fractal @ {last_down}" if last_down is not None else "No down fractal",
            )

        if last_down is not None and close < last_down:
            conf = _confidence(last_down)
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Fractal break down: close({close:.4f}) < down_fractal({last_down:.4f})",
                invalidation=f"Close above down fractal {last_down:.4f}",
                bull_case=f"Up fractal @ {last_up}" if last_up is not None else "No up fractal",
                bear_case=f"Lower fractal breakdown @ {last_down:.4f}",
            )

        return self._hold(df, "No fractal breakout signal")

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        close = 0.0
        if df is not None and len(df) >= 2:
            try:
                close = float(df.iloc[-2]["close"])
            except Exception:
                close = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
