"""
CCI (Commodity Channel Index) 전략:
- BUY: CCI가 -100에서 위로 크로스 (과매도 반등)
- SELL: CCI가 +100에서 아래로 크로스 (과매수 하락)
- Confidence: HIGH if |CCI| > 200, MEDIUM otherwise
- 최소 30행 필요
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 30
_UPPER = 100
_LOWER = -100
_HIGH_CONF = 200


class CCIStrategy(BaseStrategy):
    name = "cci"

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

        tp = (df["high"] + df["low"] + df["close"]) / 3
        mean_tp = tp.rolling(_PERIOD).mean()
        mean_dev = tp.rolling(_PERIOD).apply(lambda x: np.mean(np.abs(x - x.mean())))
        cci = (tp - mean_tp) / (0.015 * mean_dev)

        cci_now = float(cci.iloc[idx])
        cci_prev = float(cci.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])

        # BUY: -100 상향 크로스
        if cci_prev <= _LOWER and cci_now > _LOWER:
            conf = Confidence.HIGH if abs(cci_now) > _HIGH_CONF else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CCI 과매도 반등: CCI {cci_prev:.1f} → {cci_now:.1f} (-100 상향 크로스)",
                invalidation=f"CCI 재하락 시 (-100 이하)",
                bull_case=f"CCI {cci_now:.1f}, 과매도 구간 탈출",
                bear_case="단순 반등일 수 있음",
            )

        # SELL: +100 하향 크로스
        if cci_prev >= _UPPER and cci_now < _UPPER:
            conf = Confidence.HIGH if abs(cci_now) > _HIGH_CONF else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CCI 과매수 하락: CCI {cci_prev:.1f} → {cci_now:.1f} (+100 하향 크로스)",
                invalidation=f"CCI 재상승 시 (+100 이상)",
                bull_case="단순 조정일 수 있음",
                bear_case=f"CCI {cci_now:.1f}, 과매수 구간 이탈",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"CCI 중립: {cci_now:.1f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
