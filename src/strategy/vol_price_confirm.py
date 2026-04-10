"""
VolumePriceConfirmStrategy:
- 거래량이 가격 방향을 확인할 때만 신호 생성
- price_dir = sign(close - close.shift(1))
- vol_above_avg = volume > volume.rolling(20).mean()
- up_vol_days = (price_dir==1 AND vol_above_avg).rolling(5).sum()
- down_vol_days = (price_dir==-1 AND vol_above_avg).rolling(5).sum()
- BUY: up_vol_days >= 3 AND close > EMA20 AND RSI14 between 40-65
- SELL: down_vol_days >= 3 AND close < EMA20 AND RSI14 between 35-60
- confidence: up_vol_days==5 or down_vol_days==5 → HIGH, 그 외 MEDIUM
- 최소 데이터: 25행
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_MA = 20
_WINDOW = 5
_EMA_PERIOD = 20
_RSI_PERIOD = 14


def _calc_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _calc_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


class VolumePriceConfirmStrategy(BaseStrategy):
    name = "vol_price_confirm"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]
        volume = df["volume"]

        # price direction
        price_dir = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

        # volume above 20-period average
        vol_avg = volume.rolling(_VOL_MA).mean()
        vol_above_avg = volume > vol_avg

        # up/down volume days over rolling 5
        up_vol = ((price_dir == 1) & vol_above_avg).astype(float)
        down_vol = ((price_dir == -1) & vol_above_avg).astype(float)
        up_vol_days = up_vol.rolling(_WINDOW).sum()
        down_vol_days = down_vol.rolling(_WINDOW).sum()

        # EMA20 and RSI14
        ema20 = _calc_ema(close, _EMA_PERIOD)
        rsi14 = _calc_rsi(close, _RSI_PERIOD)

        idx = len(df) - 2  # _last() 기준
        c = float(close.iloc[idx])
        e20 = float(ema20.iloc[idx])
        rsi = float(rsi14.iloc[idx])
        uvd = float(up_vol_days.iloc[idx])
        dvd = float(down_vol_days.iloc[idx])

        context = (
            f"close={c:.4f} ema20={e20:.4f} rsi={rsi:.2f} "
            f"up_vol_days={uvd} down_vol_days={dvd}"
        )

        # BUY
        if uvd >= 3 and c > e20 and 40 <= rsi <= 65:
            confidence = Confidence.HIGH if uvd == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"Volume-Price BUY: up_vol_days={uvd} close({c:.4f})>ema20({e20:.4f}) "
                    f"RSI={rsi:.2f}(40-65)"
                ),
                invalidation=f"Close below EMA20 ({e20:.4f}) or RSI outside 40-65",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if dvd >= 3 and c < e20 and 35 <= rsi <= 60:
            confidence = Confidence.HIGH if dvd == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=(
                    f"Volume-Price SELL: down_vol_days={dvd} close({c:.4f})<ema20({e20:.4f}) "
                    f"RSI={rsi:.2f}(35-60)"
                ),
                invalidation=f"Close above EMA20 ({e20:.4f}) or RSI outside 35-60",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
