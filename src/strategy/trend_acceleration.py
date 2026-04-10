"""
TrendAccelerationStrategy: 추세 가속도 기반 진입 (추세가 가속될 때 추종).
- ema10 = close.ewm(span=10, adjust=False).mean()
- ema20 = close.ewm(span=20, adjust=False).mean()
- spread = ema10 - ema20
- spread_slope = spread.diff(3)
- spread_ma = spread.rolling(10, min_periods=1).mean()
- BUY:  spread > 0 AND spread > spread_ma AND spread_slope > 0
- SELL: spread < 0 AND spread < spread_ma AND spread_slope < 0
- confidence: HIGH if abs(spread_slope) > spread.rolling(20,min_periods=1).std() else MEDIUM
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25


class TrendAccelerationStrategy(BaseStrategy):
    name = "trend_acceleration"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        close_s = df["close"].iloc[: idx + 1]

        ema10 = close_s.ewm(span=10, adjust=False).mean()
        ema20 = close_s.ewm(span=20, adjust=False).mean()
        spread = ema10 - ema20
        spread_slope = spread.diff(3)
        spread_ma = spread.rolling(10, min_periods=1).mean()
        spread_std = spread.rolling(20, min_periods=1).std()

        sp = float(spread.iloc[-1])
        slope = float(spread_slope.iloc[-1])
        sp_ma = float(spread_ma.iloc[-1])
        sp_std = float(spread_std.iloc[-1]) if not pd.isna(spread_std.iloc[-1]) else 0.0
        close = float(close_s.iloc[-1])

        # NaN guard
        if pd.isna(sp) or pd.isna(slope) or pd.isna(sp_ma):
            return self._hold(df, "NaN in indicators")

        context = (
            f"close={close:.4f} spread={sp:.4f} spread_ma={sp_ma:.4f} "
            f"spread_slope={slope:.6f} spread_std={sp_std:.6f}"
        )

        if sp > 0 and sp > sp_ma and slope > 0:
            confidence = (
                Confidence.HIGH
                if abs(slope) > sp_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA 스프레드 상향 가속: spread={sp:.4f}>0, "
                    f"spread>spread_ma({sp_ma:.4f}), slope={slope:.6f}>0"
                ),
                invalidation=f"Spread crosses below 0 or spread_ma ({sp_ma:.4f})",
                bull_case=context,
                bear_case=context,
            )

        if sp < 0 and sp < sp_ma and slope < 0:
            confidence = (
                Confidence.HIGH
                if abs(slope) > sp_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"EMA 스프레드 하향 가속: spread={sp:.4f}<0, "
                    f"spread<spread_ma({sp_ma:.4f}), slope={slope:.6f}<0"
                ),
                invalidation=f"Spread crosses above 0 or spread_ma ({sp_ma:.4f})",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
