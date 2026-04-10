"""
MeanReversionEntryStrategy:
- 하락/상승 후 최적 진입 타이밍 감지
- BUY: consecutive_down >= 3 AND rsi14 < 40 AND volume > avg_vol
- SELL: consecutive_up >= 3 AND rsi14 > 60 AND volume > avg_vol
- confidence HIGH: consecutive_down >= 4 AND rsi14 < 30 (BUY)
- 최소 행: 20
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_AVG_VOL_PERIOD = 20


def _wilder_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class MeanReversionEntryStrategy(BaseStrategy):
    name = "mr_entry"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        open_ = df["open"]
        volume = df["volume"]

        is_down = (close < open_).astype(int)
        is_up = (close > open_).astype(int)
        consecutive_down = is_down.rolling(5).sum()
        consecutive_up = is_up.rolling(5).sum()

        rsi14 = _wilder_rsi(close, 14)
        avg_vol = volume.rolling(_AVG_VOL_PERIOD).mean()

        idx = len(df) - 2
        c_down = float(consecutive_down.iloc[idx])
        c_up = float(consecutive_up.iloc[idx])
        rsi = float(rsi14.iloc[idx])
        vol = float(volume.iloc[idx])
        avg_v = float(avg_vol.iloc[idx])
        price = float(close.iloc[idx])

        context = f"close={price:.4f} rsi14={rsi:.2f} c_down={c_down:.0f} c_up={c_up:.0f} vol_ratio={vol/avg_v:.2f}"

        # BUY
        if c_down >= 3 and rsi < 40 and vol > avg_v:
            if c_down >= 4 and rsi < 30:
                conf = Confidence.HIGH
            else:
                conf = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=price,
                reasoning=f"평균회귀 BUY: c_down={c_down:.0f}>=3, rsi14={rsi:.2f}<40, vol 확인",
                invalidation="rsi14 >= 40 또는 consecutive_down < 3",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if c_up >= 3 and rsi > 60 and vol > avg_v:
            conf = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=price,
                reasoning=f"평균회귀 SELL: c_up={c_up:.0f}>=3, rsi14={rsi:.2f}>60, vol 확인",
                invalidation="rsi14 <= 60 또는 consecutive_up < 3",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        idx = len(df) - 2 if len(df) >= 2 else 0
        price = float(df["close"].iloc[idx])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
