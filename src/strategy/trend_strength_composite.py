"""
TrendStrengthCompositeStrategy: ADX + EMA방향 + 거래량 가중 복합 추세 강도 전략.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class TrendStrengthCompositeStrategy(BaseStrategy):
    name = "trend_strength_composite"

    MIN_ROWS = 30

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="insufficient data",
                invalidation="need more candles",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # True Range
        tr = pd.concat(
            [
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        raw_dm_plus = (high - high.shift(1)).clip(lower=0)
        raw_dm_minus = (low.shift(1) - low).clip(lower=0)

        dm_plus = raw_dm_plus.where(raw_dm_plus > raw_dm_minus, other=0.0)
        dm_minus = raw_dm_minus.where(raw_dm_minus > raw_dm_plus, other=0.0)

        atr14 = tr.rolling(14, min_periods=1).mean()
        di_plus = dm_plus.rolling(14, min_periods=1).mean() / (atr14 + 1e-10) * 100
        di_minus = dm_minus.rolling(14, min_periods=1).mean() / (atr14 + 1e-10) * 100
        dx = (di_plus - di_minus).abs() / (di_plus + di_minus + 1e-10) * 100
        adx = dx.rolling(14, min_periods=1).mean()

        ema20 = close.ewm(span=20, adjust=False).mean()
        ema_trend = close > ema20
        vol_ma = volume.rolling(20, min_periods=1).mean()
        vol_trend = volume > vol_ma

        idx = len(df) - 2

        c = close.iloc[idx]
        adx_val = adx.iloc[idx]
        dip = di_plus.iloc[idx]
        dim = di_minus.iloc[idx]
        et = ema_trend.iloc[idx]
        vt = vol_trend.iloc[idx]

        confidence = Confidence.HIGH if adx_val > 40 else Confidence.MEDIUM

        if adx_val > 25 and et and dip > dim and vt:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c),
                reasoning=(
                    f"ADX={adx_val:.1f}>25, price above EMA20, "
                    f"DI+({dip:.1f})>DI-({dim:.1f}), volume surge"
                ),
                invalidation=f"ADX < 20 or price below EMA20",
                bull_case="strong uptrend confirmed by ADX + volume",
                bear_case="ADX could fade",
            )

        if adx_val > 25 and not et and dim > dip and vt:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c),
                reasoning=(
                    f"ADX={adx_val:.1f}>25, price below EMA20, "
                    f"DI-({dim:.1f})>DI+({dip:.1f}), volume surge"
                ),
                invalidation=f"ADX < 20 or price above EMA20",
                bull_case="potential reversal",
                bear_case="strong downtrend confirmed by ADX + volume",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(c),
            reasoning=(
                f"ADX={adx_val:.1f} or conditions not met "
                f"(ema_trend={et}, vol_trend={vt}, DI+={dip:.1f}, DI-={dim:.1f})"
            ),
            invalidation="wait for trend strength",
        )
