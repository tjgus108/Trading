"""
EMACloudStrategy: Ichimoku-inspired EMA Cloud 전략.
Tenkan/Kijun을 EMA로 대체하여 구름(cloud)을 계산.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EMACloudStrategy(BaseStrategy):
    name = "ema_cloud"

    MIN_ROWS = 60

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

        fast_line = close.ewm(span=9, adjust=False).mean()
        slow_line = close.ewm(span=26, adjust=False).mean()

        cloud_top = fast_line.combine(slow_line, max)
        cloud_bottom = fast_line.combine(slow_line, min)

        cloud_top_future = cloud_top.shift(26)
        cloud_bottom_future = cloud_bottom.shift(26)

        idx = len(df) - 2

        c = close.iloc[idx]
        fl = fast_line.iloc[idx]
        sl = slow_line.iloc[idx]
        ct = cloud_top.iloc[idx]
        cb = cloud_bottom.iloc[idx]
        ctf = cloud_top_future.iloc[idx]
        cbf = cloud_bottom_future.iloc[idx]

        if pd.isna(ctf) or pd.isna(cbf):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(c),
                reasoning="cloud_future NaN — insufficient history",
                invalidation="need more candles",
            )

        separation = abs(fl - sl) / (c + 1e-10)
        confidence = Confidence.HIGH if separation > 0.02 else Confidence.MEDIUM

        if c > ct and fl > sl and c > ctf:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c),
                reasoning=(
                    f"close({c:.4f}) > cloud_top({ct:.4f}), "
                    f"fast({fl:.4f}) > slow({sl:.4f}), "
                    f"close > cloud_top_future({ctf:.4f})"
                ),
                invalidation=f"close < cloud_bottom({cb:.4f})",
                bull_case="price above full cloud, bullish momentum",
                bear_case="cloud could compress",
            )

        if c < cb and fl < sl and c < cbf:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c),
                reasoning=(
                    f"close({c:.4f}) < cloud_bottom({cb:.4f}), "
                    f"fast({fl:.4f}) < slow({sl:.4f}), "
                    f"close < cloud_bottom_future({cbf:.4f})"
                ),
                invalidation=f"close > cloud_top({ct:.4f})",
                bull_case="potential reversal from oversold",
                bear_case="price below full cloud, bearish momentum",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(c),
            reasoning="price inside or near cloud — no clear signal",
            invalidation="wait for breakout",
        )
