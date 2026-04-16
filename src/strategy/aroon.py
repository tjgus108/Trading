"""
Aroon Oscillator 기반 추세 전환 전략.
- Aroon Up   = 100 * (period-1 - periods_since_period_high) / (period-1)
- Aroon Down = 100 * (period-1 - periods_since_period_low)  / (period-1)
- Aroon Oscillator = Aroon Up - Aroon Down
- BUY:  Aroon Up >= 70 AND Aroon Down <= 30
- SELL: Aroon Down >= 70 AND Aroon Up <= 30
- confidence: HIGH if (Up==100 or Down==100), MEDIUM otherwise
- 최소 데이터: 30행
"""

from typing import Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_PERIOD = 25


def _aroon(df: pd.DataFrame, idx: int, period: int = _PERIOD) -> Tuple[float, float]:
    """idx 위치 기준 25봉 슬라이스에서 Aroon Up/Down 계산."""
    high_slice = df["high"].iloc[idx - period + 1: idx + 1]
    low_slice = df["low"].iloc[idx - period + 1: idx + 1]
    aroon_up = 100 * (period - 1 - high_slice.values[::-1].argmax()) / (period - 1)
    aroon_down = 100 * (period - 1 - low_slice.values[::-1].argmin()) / (period - 1)
    return float(aroon_up), float(aroon_down)


class AroonStrategy(BaseStrategy):
    name = "aroon"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for Aroon (need 30 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]
        if idx < _PERIOD - 1:
            return self._hold(df, "Insufficient data for Aroon period")

        aroon_up, aroon_down = _aroon(df, idx, _PERIOD)
        last = self._last(df)
        close = float(last["close"])
        context = f"close={close:.2f} aroon_up={aroon_up:.1f} aroon_down={aroon_down:.1f}"

        # BUY: 강한 상승 추세 시작
        if aroon_up >= 70 and aroon_down <= 30:
            confidence = Confidence.HIGH if (aroon_up == 100 or aroon_down == 100) else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Aroon 강한 상승 추세: Up={aroon_up:.1f}(>=70), Down={aroon_down:.1f}(<=30)"
                ),
                invalidation="Aroon Up < 70 또는 Aroon Down > 30",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 강한 하락 추세 시작
        if aroon_down >= 70 and aroon_up <= 30:
            confidence = Confidence.HIGH if (aroon_down == 100 or aroon_up == 100) else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Aroon 강한 하락 추세: Down={aroon_down:.1f}(>=70), Up={aroon_up:.1f}(<=30)"
                ),
                invalidation="Aroon Down < 70 또는 Aroon Up > 30",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: aroon_up={aroon_up:.1f} aroon_down={aroon_down:.1f}",
                          context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
