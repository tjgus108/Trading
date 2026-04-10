"""
VolatilityTrendStrategy: 변동성 확장 + 추세 방향 기반 진입 전략.
ATR이 ATR MA를 초과하고 기울기가 양수일 때 close_ma 방향으로 진입.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VolatilityTrendStrategy(BaseStrategy):
    name = "volatility_trend"

    _MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self._MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Insufficient data",
                invalidation="",
            )

        high = df["high"]
        low = df["low"]
        close = df["close"]

        atr = (high - low).rolling(14, min_periods=1).mean()
        atr_ma = atr.rolling(10, min_periods=1).mean()
        atr_slope = atr.diff(5)
        close_ma = close.ewm(span=20, adjust=False).mean()

        idx = len(df) - 2
        last = self._last(df)

        entry = float(last["close"])
        atr_v = float(atr.iloc[idx])
        atr_ma_v = float(atr_ma.iloc[idx])
        atr_slope_v = float(atr_slope.iloc[idx])
        close_ma_v = float(close_ma.iloc[idx])

        if any(pd.isna(v) for v in [entry, atr_v, atr_ma_v, atr_slope_v, close_ma_v]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN detected",
                invalidation="",
            )

        bull_case = (
            f"ATR={atr_v:.4f} ATR_MA={atr_ma_v:.4f} slope={atr_slope_v:.4f} "
            f"close={entry:.2f} close_ma={close_ma_v:.2f}"
        )
        bear_case = bull_case

        expanding = atr_v > atr_ma_v
        slope_up = atr_slope_v > 0
        conf = Confidence.HIGH if atr_v > atr_ma_v * 1.5 else Confidence.MEDIUM

        if expanding and slope_up and entry > close_ma_v:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Volatility expanding (ATR {atr_v:.4f} > ATR_MA {atr_ma_v:.4f}), "
                    f"slope positive, close above EMA20"
                ),
                invalidation=f"Close below EMA20 ({close_ma_v:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if expanding and slope_up and entry < close_ma_v:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Volatility expanding (ATR {atr_v:.4f} > ATR_MA {atr_ma_v:.4f}), "
                    f"slope positive, close below EMA20"
                ),
                invalidation=f"Close above EMA20 ({close_ma_v:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"Volatility contracting or slope flat: "
                f"ATR={atr_v:.4f} ATR_MA={atr_ma_v:.4f} slope={atr_slope_v:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
