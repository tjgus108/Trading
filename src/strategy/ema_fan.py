"""
EMAFan 전략:
- EMA 5/10/20/50이 부채꼴 형태로 완전 정렬된 강한 추세 확인
- BUY:  bullish_fan AND fan_spread > fan_spread_ma (팬 확대 중)
- SELL: bearish_fan AND fan_spread > fan_spread_ma
- confidence: HIGH if fan_spread > fan_spread_ma * 1.5, MEDIUM otherwise
- 최소 데이터: 55행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55


class EMAFanStrategy(BaseStrategy):
    name = "ema_fan"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        close = df["close"]

        ema5 = close.ewm(span=5, adjust=False).mean()
        ema10 = close.ewm(span=10, adjust=False).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        bullish_fan = (ema5 > ema10) & (ema10 > ema20) & (ema20 > ema50)
        bearish_fan = (ema5 < ema10) & (ema10 < ema20) & (ema20 < ema50)

        fan_spread = (ema5 - ema50).abs() / close
        fan_spread_ma = fan_spread.rolling(10, min_periods=1).mean()

        idx = len(df) - 2

        is_bullish = bool(bullish_fan.iloc[idx])
        is_bearish = bool(bearish_fan.iloc[idx])
        fs = float(fan_spread.iloc[idx])
        fs_ma = float(fan_spread_ma.iloc[idx])
        c = float(close.iloc[idx])
        e5 = float(ema5.iloc[idx])
        e10 = float(ema10.iloc[idx])
        e20 = float(ema20.iloc[idx])
        e50 = float(ema50.iloc[idx])

        if pd.isna(fs) or pd.isna(fs_ma) or fs_ma == 0:
            return self._hold(df, "NaN in indicators")

        context = (
            f"close={c:.2f} ema5={e5:.2f} ema10={e10:.2f} ema20={e20:.2f} ema50={e50:.2f} "
            f"fan_spread={fs:.4f} fan_spread_ma={fs_ma:.4f}"
        )

        # BUY
        if is_bullish and fs > fs_ma:
            confidence = Confidence.HIGH if fs > fs_ma * 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"EMAFan BUY: 강세 부채꼴 정렬 + 팬 확대 (spread={fs:.4f} > ma={fs_ma:.4f})",
                invalidation="EMA 배열 무너짐 또는 팬 수축",
                bull_case=context,
                bear_case=context,
            )

        # SELL
        if is_bearish and fs > fs_ma:
            confidence = Confidence.HIGH if fs > fs_ma * 1.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=c,
                reasoning=f"EMAFan SELL: 약세 부채꼴 정렬 + 팬 확대 (spread={fs:.4f} > ma={fs_ma:.4f})",
                invalidation="EMA 배열 무너짐 또는 팬 수축",
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
