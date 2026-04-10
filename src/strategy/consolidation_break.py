"""
ConsolidationBreak 전략:
- 횡보 후 돌파 전략
- BUY: consolidating.shift(1) AND close > hi.shift(1)
- SELL: consolidating.shift(1) AND close < lo.shift(1)
- confidence: HIGH if volume > vol_ma*1.5 AND range_width < range_ma*0.4, else MEDIUM
- 최소 행: 25
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_LOOKBACK = 10
_CONSOLIDATION_RATIO = 0.6
_HIGH_CONF_VOL_MULT = 1.5
_HIGH_CONF_RANGE_RATIO = 0.4


class ConsolidationBreakStrategy(BaseStrategy):
    name = "consolidation_break"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        hi = high.rolling(_LOOKBACK, min_periods=1).max()
        lo = low.rolling(_LOOKBACK, min_periods=1).min()
        range_width = hi - lo
        range_ma = range_width.rolling(20, min_periods=1).mean()
        consolidating = range_width < range_ma * _CONSOLIDATION_RATIO
        vol_ma = volume.rolling(10, min_periods=1).mean()

        row = self._last(df)
        idx = len(df) - 2

        close_val = float(row["close"])
        vol_val = float(row["volume"])
        vol_ma_val = float(vol_ma.iloc[idx])
        range_width_val = float(range_width.iloc[idx])
        range_ma_val = float(range_ma.iloc[idx])

        # 이전 봉 기준 (shift(1) → idx-1)
        consol_prev = bool(consolidating.iloc[idx - 1]) if idx >= 1 else False
        hi_prev = float(hi.iloc[idx - 1]) if idx >= 1 else float("nan")
        lo_prev = float(lo.iloc[idx - 1]) if idx >= 1 else float("nan")

        # NaN 체크
        if any(v != v for v in [close_val, vol_val, vol_ma_val, range_width_val, range_ma_val, hi_prev, lo_prev]):
            return self._hold(df, "NaN detected")

        high_conf = vol_val > vol_ma_val * _HIGH_CONF_VOL_MULT and range_width_val < range_ma_val * _HIGH_CONF_RANGE_RATIO

        buy_signal = consol_prev and close_val > hi_prev
        sell_signal = consol_prev and close_val < lo_prev

        if buy_signal:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Consolidation break up: close={close_val:.2f} > hi_prev={hi_prev:.2f}, "
                    f"range_width={range_width_val:.4f} vs range_ma={range_ma_val:.4f}"
                ),
                invalidation=f"Close back below consolidation high ({hi_prev:.2f})",
                bull_case="Breakout from tight consolidation",
                bear_case="False breakout possible",
            )

        if sell_signal:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Consolidation break down: close={close_val:.2f} < lo_prev={lo_prev:.2f}, "
                    f"range_width={range_width_val:.4f} vs range_ma={range_ma_val:.4f}"
                ),
                invalidation=f"Close back above consolidation low ({lo_prev:.2f})",
                bull_case="False breakdown possible",
                bear_case="Breakdown from tight consolidation",
            )

        return self._hold(
            df,
            f"No breakout: consol_prev={consol_prev}, "
            f"close={close_val:.2f}, hi_prev={hi_prev:.2f}, lo_prev={lo_prev:.2f}",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df.iloc[-2]["close"]) if len(df) >= 2 else float(df.iloc[-1]["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
