"""
WickReversalStrategy: 긴 꼬리(wick)를 이용한 반전 감지.
- Hammer (lower_wick_ratio > 0.6, close > SMA20*0.97) → BUY
- Shooting Star (upper_wick_ratio > 0.6, close < SMA20*1.03) → SELL
- volume > avg_volume_10 * 0.8
- wick_ratio > 0.7 → HIGH confidence
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class WickReversalStrategy(BaseStrategy):
    name = "wick_reversal"

    MIN_ROWS = 15

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < self.MIN_ROWS:
            hold.reasoning = "데이터 부족"
            return hold

        last = self._last(df)
        entry = float(last["close"])
        hold.entry_price = entry

        high = float(last["high"])
        low = float(last["low"])
        open_ = float(last["open"])
        close = float(last["close"])
        volume = float(last["volume"])

        total_range = high - low
        if total_range == 0:
            hold.reasoning = "total_range=0, 캔들 이상"
            return hold

        lower_wick = min(open_, close) - low
        upper_wick = high - max(open_, close)

        lower_wick_ratio = lower_wick / total_range
        upper_wick_ratio = upper_wick / total_range

        # SMA20
        lookback = min(20, len(df) - 1)
        sma20 = float(df["close"].iloc[-lookback - 1:-1].mean())

        # avg volume 10
        vol_lookback = min(10, len(df) - 1)
        avg_vol_10 = float(df["volume"].iloc[-vol_lookback - 1:-1].mean())
        vol_ok = volume > avg_vol_10 * 0.8

        bull_case = (
            f"lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}"
        )
        bear_case = (
            f"upper_wick_ratio={upper_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}"
        )

        # Hammer: BUY
        hammer = lower_wick_ratio > 0.6 and close > sma20 * 0.97 and vol_ok
        if hammer:
            confidence = Confidence.HIGH if lower_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Hammer 패턴: lower_wick_ratio={lower_wick_ratio:.3f} > 0.6, "
                    f"close({close:.4f}) > SMA20*0.97({sma20*0.97:.4f}), vol_ok={vol_ok}"
                ),
                invalidation=f"Close below SMA20*0.97 ({sma20*0.97:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # Shooting Star: SELL
        shooting_star = upper_wick_ratio > 0.6 and close < sma20 * 1.03 and vol_ok
        if shooting_star:
            confidence = Confidence.HIGH if upper_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Shooting Star 패턴: upper_wick_ratio={upper_wick_ratio:.3f} > 0.6, "
                    f"close({close:.4f}) < SMA20*1.03({sma20*1.03:.4f}), vol_ok={vol_ok}"
                ),
                invalidation=f"Close above SMA20*1.03 ({sma20*1.03:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = (
            f"패턴 없음: lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"upper_wick_ratio={upper_wick_ratio:.3f}, vol_ok={vol_ok}"
        )
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold
