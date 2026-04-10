"""
TrendBreakConfirmStrategy: 추세선 돌파 + 재확인 진입.
EMA20 돌파 후 3봉 내 재확인 + EMA20/50 방향 + 거래량 확인.
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendBreakConfirmStrategy(BaseStrategy):
    name = "trend_break_confirm"

    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: minimum {self.MIN_ROWS} rows required",
                invalidation="",
            )

        close = df["close"]
        volume = df["volume"]

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        broke_above_ema20 = (close > ema20) & (close.shift(1) <= ema20.shift(1))
        broke_below_ema20 = (close < ema20) & (close.shift(1) >= ema20.shift(1))

        confirmed_bull = (
            broke_above_ema20.rolling(3, min_periods=1).max().astype(bool)
            & (ema20 > ema50)
        )
        confirmed_bear = (
            broke_below_ema20.rolling(3, min_periods=1).max().astype(bool)
            & (ema20 < ema50)
        )

        vol_ma10 = volume.rolling(10, min_periods=1).mean()
        vol_confirm = volume > vol_ma10

        idx = len(df) - 2
        last = df.iloc[idx]

        c = close.iloc[idx]
        e20 = ema20.iloc[idx]
        e50 = ema50.iloc[idx]
        cb = confirmed_bull.iloc[idx]
        cbe = confirmed_bear.iloc[idx]
        vc = vol_confirm.iloc[idx]

        # NaN 체크
        if any(v is None or (isinstance(v, float) and np.isnan(v))
               for v in [c, e20, e50]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=float(c) if c and not np.isnan(c) else 0.0,
                reasoning="NaN values detected in indicators",
                invalidation="",
            )

        buy_signal = bool(cb) and bool(vc) and (c > e20)
        sell_signal = bool(cbe) and bool(vc) and (c < e20)

        entry = float(c)

        if buy_signal:
            confidence = Confidence.HIGH if c > e50 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 breakout confirmed (bull). "
                    f"EMA20={e20:.4f} EMA50={e50:.4f} close={c:.4f} vol_confirm={vc}"
                ),
                invalidation=f"Close below EMA20 ({e20:.4f})",
                bull_case=f"EMA20 > EMA50, close above EMA20, volume surge",
                bear_case=f"EMA50={e50:.4f} resistance above",
            )

        if sell_signal:
            confidence = Confidence.HIGH if c < e50 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"EMA20 breakdown confirmed (bear). "
                    f"EMA20={e20:.4f} EMA50={e50:.4f} close={c:.4f} vol_confirm={vc}"
                ),
                invalidation=f"Close above EMA20 ({e20:.4f})",
                bull_case=f"EMA50={e50:.4f} support below",
                bear_case=f"EMA20 < EMA50, close below EMA20, volume surge",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"No confirmed breakout. "
                f"confirmed_bull={cb} confirmed_bear={cbe} vol_confirm={vc} "
                f"close={'above' if c > e20 else 'below'} EMA20"
            ),
            invalidation="",
            bull_case=f"EMA20={e20:.4f} EMA50={e50:.4f}",
            bear_case=f"EMA20={e20:.4f} EMA50={e50:.4f}",
        )
