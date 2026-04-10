"""
GapMomentum 전략:
- 갭 발생 후 모멘텀 지속 전략
- BUY: gap_up_pct > 0.3 AND close > open AND volume > vol_ma
- SELL: gap_down_pct > 0.3 AND close < open AND volume > vol_ma
- confidence: HIGH if gap_pct > 1.0, else MEDIUM
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_GAP_THRESHOLD = 0.3
_GAP_HIGH = 1.0


class GapMomentumStrategy(BaseStrategy):
    name = "gap_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        open_ = df["open"]
        close = df["close"]
        volume = df["volume"]

        gap_up = open_ - close.shift(1)
        gap_down = close.shift(1) - open_
        gap_up_pct = gap_up / (close.shift(1) + 1e-10) * 100
        gap_down_pct = gap_down / (close.shift(1) + 1e-10) * 100
        vol_ma = volume.rolling(10, min_periods=1).mean()

        row = self._last(df)
        idx = len(df) - 2

        gu_pct = float(gap_up_pct.iloc[idx])
        gd_pct = float(gap_down_pct.iloc[idx])
        close_val = float(row["close"])
        open_val = float(row["open"])
        vol_val = float(row["volume"])
        vol_ma_val = float(vol_ma.iloc[idx])

        # NaN 체크
        if any(
            v != v for v in [gu_pct, gd_pct, close_val, open_val, vol_val, vol_ma_val]
        ):
            return self._hold(df, "NaN detected")

        buy_signal = gu_pct > _GAP_THRESHOLD and close_val > open_val and vol_val > vol_ma_val
        sell_signal = gd_pct > _GAP_THRESHOLD and close_val < open_val and vol_val > vol_ma_val

        if buy_signal:
            confidence = Confidence.HIGH if gu_pct > _GAP_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Gap up {gu_pct:.2f}%, bullish candle, "
                    f"vol={vol_val:.0f} > vol_ma={vol_ma_val:.0f}"
                ),
                invalidation=f"Close below prev_close ({float(close.shift(1).iloc[idx]):.2f})",
                bull_case=f"Gap momentum {gu_pct:.2f}%",
                bear_case="Gap may fill",
            )

        if sell_signal:
            confidence = Confidence.HIGH if gd_pct > _GAP_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Gap down {gd_pct:.2f}%, bearish candle, "
                    f"vol={vol_val:.0f} > vol_ma={vol_ma_val:.0f}"
                ),
                invalidation=f"Close above prev_close ({float(close.shift(1).iloc[idx]):.2f})",
                bull_case="Gap may fill (mean reversion)",
                bear_case=f"Gap down momentum {gd_pct:.2f}%",
            )

        return self._hold(
            df,
            f"No gap signal: gap_up={gu_pct:.2f}%, gap_down={gd_pct:.2f}%, "
            f"close={'>' if close_val > open_val else '<'} open, vol_ok={vol_val > vol_ma_val}",
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
