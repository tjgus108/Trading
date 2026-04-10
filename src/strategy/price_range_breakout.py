"""
PriceRangeBreakout 전략:
- 일정 기간 range 압축 후 확장 돌파 감지
- range_high = high.rolling(15).max()
- range_low  = low.rolling(15).min()
- range_width = range_high - range_low
- range_ma    = range_width.rolling(20).mean()
- compression = range_width < range_ma * 0.7
- BUY:  compression AND close > range_high.shift(1)
- SELL: compression AND close < range_low.shift(1)
- confidence: HIGH if range_width < range_ma * 0.5 else MEDIUM
- 최소 행: 25
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_RANGE_WINDOW = 15
_MA_WINDOW = 20
_COMPRESS_THRESH = 0.7
_HIGH_THRESH = 0.5


class PriceRangeBreakoutStrategy(BaseStrategy):
    name = "price_range_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(0.0, "데이터 부족", "", "")

        idx = len(df) - 2

        high = df["high"]
        low = df["low"]
        close = df["close"]

        range_high = high.rolling(_RANGE_WINDOW, min_periods=1).max()
        range_low = low.rolling(_RANGE_WINDOW, min_periods=1).min()
        range_width = range_high - range_low
        range_ma = range_width.rolling(_MA_WINDOW, min_periods=1).mean()

        compression = range_width < range_ma * _COMPRESS_THRESH

        rw_now = float(range_width.iloc[idx])
        rm_now = float(range_ma.iloc[idx])
        rh_prev = float(range_high.iloc[idx - 1]) if idx >= 1 else float(range_high.iloc[idx])
        rl_prev = float(range_low.iloc[idx - 1]) if idx >= 1 else float(range_low.iloc[idx])
        comp_now = bool(compression.iloc[idx])
        close_now = float(close.iloc[idx])

        # NaN 체크
        if any(v != v for v in (rw_now, rm_now, rh_prev, rl_prev, close_now)):
            return self._hold(close_now, "NaN 값 감지", "", "")

        conf = Confidence.HIGH if rw_now < rm_now * _HIGH_THRESH else Confidence.MEDIUM

        bull_case = (
            f"compression={comp_now}, close={close_now:.4f}, "
            f"range_high(prev)={rh_prev:.4f}, range_width={rw_now:.4f}, range_ma={rm_now:.4f}"
        )
        bear_case = (
            f"compression={comp_now}, close={close_now:.4f}, "
            f"range_low(prev)={rl_prev:.4f}, range_width={rw_now:.4f}, range_ma={rm_now:.4f}"
        )

        if comp_now and close_now > rh_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Range 압축 후 상향 돌파: close({close_now:.4f}) > range_high_prev({rh_prev:.4f}), "
                    f"range_width({rw_now:.4f}) < range_ma({rm_now:.4f})*{_COMPRESS_THRESH}"
                ),
                invalidation=f"Close back below range_high_prev ({rh_prev:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if comp_now and close_now < rl_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"Range 압축 후 하향 돌파: close({close_now:.4f}) < range_low_prev({rl_prev:.4f}), "
                    f"range_width({rw_now:.4f}) < range_ma({rm_now:.4f})*{_COMPRESS_THRESH}"
                ),
                invalidation=f"Close back above range_low_prev ({rl_prev:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reason = (
            f"No breakout. compression={comp_now}, close={close_now:.4f}, "
            f"range_high_prev={rh_prev:.4f}, range_low_prev={rl_prev:.4f}"
        )
        return self._hold(close_now, reason, bull_case, bear_case)

    def _hold(self, entry: float, reason: str, bull_case: str, bear_case: str) -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
