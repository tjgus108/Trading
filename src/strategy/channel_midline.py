"""
ChannelMidlineStrategy: 20봉 가격 채널의 중심선(midline) 돌파 기반 매매 전략.
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class ChannelMidlineStrategy(BaseStrategy):
    name = "channel_midline"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < 25:
            price = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=price,
                reasoning="Insufficient data (need at least 25 rows).",
                invalidation="",
            )

        idx = len(df) - 2

        highest = df["high"].rolling(20).max()
        lowest = df["low"].rolling(20).min()
        midline = (highest + lowest) / 2
        channel_width = highest - lowest

        prev_close = float(df["close"].iloc[idx - 1])
        curr_close = float(df["close"].iloc[idx])
        mid_val = float(midline.iloc[idx])
        cw_val = float(channel_width.iloc[idx])
        cw_mean = float(channel_width.rolling(20).mean().iloc[idx])

        if any(pd.isna(v) for v in [prev_close, curr_close, mid_val, cw_val, cw_mean]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=curr_close if not pd.isna(curr_close) else 0.0,
                reasoning="NaN in indicator values.",
                invalidation="",
            )

        conf = Confidence.HIGH if cw_val > cw_mean * 1.3 else Confidence.MEDIUM

        if prev_close < mid_val and curr_close > mid_val:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"Midline crossover upward. prev_close={prev_close:.4f} < midline={mid_val:.4f}, "
                    f"curr_close={curr_close:.4f} > midline. channel_width={cw_val:.4f}."
                ),
                invalidation=f"Close back below midline ({mid_val:.4f})",
                bull_case=f"Channel midline breakout with channel_width={cw_val:.4f}.",
                bear_case=f"May be a false breakout if channel is narrow.",
            )

        if prev_close > mid_val and curr_close < mid_val:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=(
                    f"Midline crossover downward. prev_close={prev_close:.4f} > midline={mid_val:.4f}, "
                    f"curr_close={curr_close:.4f} < midline. channel_width={cw_val:.4f}."
                ),
                invalidation=f"Close back above midline ({mid_val:.4f})",
                bull_case=f"Midline={mid_val:.4f}.",
                bear_case=f"Channel midline breakdown. channel_width={cw_val:.4f}.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=curr_close,
            reasoning=(
                f"No midline crossover. prev_close={prev_close:.4f}, curr_close={curr_close:.4f}, "
                f"midline={mid_val:.4f}, channel_width={cw_val:.4f}."
            ),
            invalidation="",
            bull_case=f"Midline={mid_val:.4f}",
            bear_case=f"Midline={mid_val:.4f}",
        )
