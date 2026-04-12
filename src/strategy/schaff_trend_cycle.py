"""
SchaffTrendCycleStrategy: STC — MACD에 Stochastic을 적용한 사이클 지표.
- BUY: stc crosses above 25 (이전 < 25, 현재 >= 25)
- SELL: stc crosses below 75 (이전 > 75, 현재 <= 75)
- confidence: HIGH if stc < 10 (BUY) or stc > 90 (SELL) else MEDIUM
- 최소 65행 필요
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 65
_BUY_LEVEL = 25
_SELL_LEVEL = 75
_HIGH_BUY = 10
_HIGH_SELL = 90


def _calc_stc(close: pd.Series) -> pd.Series:
    # 1. MACD
    ema23 = close.ewm(span=23, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    macd = ema23 - ema50

    # 2. Stochastic of MACD (10 period)
    macd_min = macd.rolling(10).min()
    macd_max = macd.rolling(10).max()
    denom = macd_max - macd_min
    stoch_macd = (macd - macd_min) / denom.where(denom != 0, other=1e-10) * 100
    stoch_macd = stoch_macd.fillna(50)

    # 3. Smooth with EWM
    k1 = stoch_macd.ewm(alpha=0.5, adjust=False).mean()

    # 4. Stochastic of K1
    k1_min = k1.rolling(10).min()
    k1_max = k1.rolling(10).max()
    denom2 = k1_max - k1_min
    stoch_k1 = (k1 - k1_min) / denom2.where(denom2 != 0, other=1e-10) * 100
    stoch_k1 = stoch_k1.fillna(50)

    # 5. STC
    stc = stoch_k1.ewm(alpha=0.5, adjust=False).mean()
    return stc


class SchaffTrendCycleStrategy(BaseStrategy):
    name = "schaff_trend_cycle"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (min 65 rows required)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        stc = _calc_stc(df["close"])

        idx = len(df) - 2
        stc_now = float(stc.iloc[idx])
        stc_prev = float(stc.iloc[idx - 1])
        entry = float(df["close"].iloc[idx])

        # BUY: stc crosses above 25
        if stc_prev < _BUY_LEVEL and stc_now >= _BUY_LEVEL:
            conf = Confidence.HIGH if stc_now < _HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"STC crosses above {_BUY_LEVEL}: {stc_prev:.2f} → {stc_now:.2f} "
                    f"(과매도 탈출)"
                ),
                invalidation=f"STC drops back below {_BUY_LEVEL}",
                bull_case=f"STC={stc_now:.2f} 과매도 탈출 신호",
                bear_case="추세 지속 가능성 있음",
            )

        # SELL: stc crosses below 75
        if stc_prev > _SELL_LEVEL and stc_now <= _SELL_LEVEL:
            conf = Confidence.HIGH if stc_now > _HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"STC crosses below {_SELL_LEVEL}: {stc_prev:.2f} → {stc_now:.2f} "
                    f"(과매수 이탈)"
                ),
                invalidation=f"STC rises back above {_SELL_LEVEL}",
                bull_case="단기 반등 가능성 있음",
                bear_case=f"STC={stc_now:.2f} 과매수 이탈 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"STC neutral: {stc_now:.2f} (prev={stc_prev:.2f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )
