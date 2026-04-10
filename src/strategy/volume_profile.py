"""
VolumeProfileStrategy:
- POC(Point of Control): 가격대별 거래량 집계에서 가장 많은 거래량의 버킷 중간 가격
- BUY: close < poc_price * 0.99 AND close > close_prev (POC 아래서 반등)
- SELL: close > poc_price * 1.01 AND close < close_prev (POC 위에서 반락)
- HOLD: 그 외
- confidence: HIGH if |close - poc_price| / poc_price > 0.02 else MEDIUM
- 최소 데이터: 25행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 20


class VolumeProfileStrategy(BaseStrategy):
    name = "volume_profile"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            reason = "Insufficient data for volume profile"
            if df is not None and len(df) >= 2:
                last = self._last(df)
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.LOW,
                    strategy=self.name,
                    entry_price=float(last["close"]),
                    reasoning=reason,
                    invalidation="",
                )
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
            )

        idx = len(df) - 2
        last = df.iloc[idx]
        prev = df.iloc[idx - 1]

        close = float(last["close"])
        close_prev = float(prev["close"])

        recent = df.iloc[max(0, idx - 19):idx + 1]
        lo = float(recent["low"].min())
        hi = float(recent["high"].max())

        if hi == lo:
            return self._hold(df, "No range for volume profile")

        buckets = np.linspace(lo, hi, 11)  # 10 버킷
        vol_by_bucket = np.zeros(10)
        for _, row in recent.iterrows():
            b = min(int((float(row["close"]) - lo) / (hi - lo) * 10), 9)
            vol_by_bucket[b] += float(row["volume"])

        poc_bucket = int(np.argmax(vol_by_bucket))
        poc_price = (buckets[poc_bucket] + buckets[poc_bucket + 1]) / 2

        dist_ratio = abs(close - poc_price) / poc_price if poc_price != 0 else 0.0
        confidence = Confidence.HIGH if dist_ratio > 0.02 else Confidence.MEDIUM

        if close < poc_price * 0.99 and close > close_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"POC 아래 반등: close={close:.4f} < poc={poc_price:.4f}*0.99, close > prev_close={close_prev:.4f}",
                invalidation=f"Close falls below {lo:.4f}",
                bull_case=f"poc={poc_price:.4f} dist={dist_ratio:.4f}",
                bear_case=f"poc={poc_price:.4f}",
            )

        if close > poc_price * 1.01 and close < close_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"POC 위 반락: close={close:.4f} > poc={poc_price:.4f}*1.01, close < prev_close={close_prev:.4f}",
                invalidation=f"Close rises above {hi:.4f}",
                bull_case=f"poc={poc_price:.4f}",
                bear_case=f"poc={poc_price:.4f} dist={dist_ratio:.4f}",
            )

        return self._hold(df, f"POC 근처 HOLD: close={close:.4f} poc={poc_price:.4f}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=reason,
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
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
