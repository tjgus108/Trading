"""
CCI Breakout 전략:
- CCI = (Typical Price - SMA20) / (0.015 * Mean Deviation)
- Typical Price = (high + low + close) / 3
- BUY:  CCI crosses above +100 (이전봉 < +100, 현재봉 >= +100)
- SELL: CCI crosses below -100 (이전봉 > -100, 현재봉 <= -100)
- confidence: HIGH if |CCI| > 150, MEDIUM if > 100
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 25
_UPPER = 100
_LOWER = -100
_HIGH_CONF = 150


def _calc_cci(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mean_tp = tp.rolling(_PERIOD).mean()
    mean_dev = tp.rolling(_PERIOD).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
    return (tp - mean_tp) / (0.015 * mean_dev)


class CCIBreakoutStrategy(BaseStrategy):
    name = "cci_breakout"

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

        cci = _calc_cci(df)
        idx = len(df) - 2
        cci_now = float(cci.iloc[idx])
        cci_prev = float(cci.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: CCI crosses above +100
        if cci_prev < _UPPER and cci_now >= _UPPER:
            conf = Confidence.HIGH if abs(cci_now) > _HIGH_CONF else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CCI +100 상향 돌파: {cci_prev:.1f} → {cci_now:.1f}",
                invalidation=f"CCI +100 이하 재하락",
                bull_case=f"CCI {cci_now:.1f}, 강세 모멘텀 진입",
                bear_case="단기 과매수 주의",
            )

        # SELL: CCI crosses below -100
        if cci_prev > _LOWER and cci_now <= _LOWER:
            conf = Confidence.HIGH if abs(cci_now) > _HIGH_CONF else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"CCI -100 하향 돌파: {cci_prev:.1f} → {cci_now:.1f}",
                invalidation=f"CCI -100 이상 재상승",
                bull_case="단기 과매도 주의",
                bear_case=f"CCI {cci_now:.1f}, 약세 모멘텀 진입",
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
