"""
SupertrendRSIStrategy: Supertrend + RSI14 복합 전략.
Supertrend bullish + RSI 50~70 → BUY
Supertrend bearish + RSI 30~50 → SELL
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25


class SupertrendRSIStrategy(BaseStrategy):
    name = "supertrend_rsi"

    def __init__(self, atr_span: int = 10, multiplier: float = 3.0, rsi_period: int = 14):
        self.atr_span = atr_span
        self.multiplier = multiplier
        self.rsi_period = rsi_period

    def _calc_atr(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr.ewm(span=self.atr_span, adjust=False).mean()

    def _calc_supertrend(self, df: pd.DataFrame) -> pd.Series:
        """True = bullish (close > supertrend line)."""
        atr = self._calc_atr(df)
        hl2 = (df["high"] + df["low"]) / 2

        basic_upper = hl2 + self.multiplier * atr
        basic_lower = hl2 - self.multiplier * atr

        upper = basic_upper.copy()
        lower = basic_lower.copy()
        trend = pd.Series(True, index=df.index)

        for i in range(1, len(df)):
            prev_upper = upper.iloc[i - 1]
            prev_lower = lower.iloc[i - 1]
            close_prev = df["close"].iloc[i - 1]

            cur_upper = basic_upper.iloc[i]
            upper.iloc[i] = cur_upper if (cur_upper < prev_upper or close_prev > prev_upper) else prev_upper

            cur_lower = basic_lower.iloc[i]
            lower.iloc[i] = cur_lower if (cur_lower > prev_lower or close_prev < prev_lower) else prev_lower

            close = df["close"].iloc[i]
            prev_trend = trend.iloc[i - 1]
            if prev_trend:
                trend.iloc[i] = close >= lower.iloc[i]
            else:
                trend.iloc[i] = close > upper.iloc[i]

        # supertrend line value
        st_line = pd.Series(index=df.index, dtype=float)
        for i in range(len(df)):
            st_line.iloc[i] = lower.iloc[i] if trend.iloc[i] else upper.iloc[i]

        return trend, st_line

    def _calc_rsi(self, close: pd.Series) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(span=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(span=self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning=f"데이터 부족: {len(df)} < {MIN_ROWS}",
                invalidation="",
            )

        trend, st_line = self._calc_supertrend(df)
        rsi = self._calc_rsi(df["close"])

        last = self._last(df)  # iloc[-2]
        idx = df.index[-2]

        bullish = bool(trend.loc[idx])
        rsi_val = float(rsi.loc[idx])
        close_val = float(last["close"])
        st_val = float(st_line.loc[idx])

        # Supertrend distance %
        st_dist_pct = abs(close_val - st_val) / st_val * 100 if st_val != 0 else 0.0

        # Confidence
        high_conf = abs(rsi_val - 50) > 15 and st_dist_pct > 1.0

        if bullish and 50 < rsi_val < 70:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Supertrend bullish, RSI={rsi_val:.1f}, ST거리={st_dist_pct:.2f}%",
                invalidation="Supertrend bearish 전환 또는 RSI < 50",
                bull_case="추세 방향 + 모멘텀 동시 확인.",
                bear_case="RSI 과매수 근접 위험.",
            )

        if (not bullish) and 30 < rsi_val < 50:
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Supertrend bearish, RSI={rsi_val:.1f}, ST거리={st_dist_pct:.2f}%",
                invalidation="Supertrend bullish 전환 또는 RSI > 50",
                bull_case="RSI 과매도 근접 반등 가능.",
                bear_case="추세 방향 + 모멘텀 동시 하락 확인.",
            )

        direction = "bullish" if bullish else "bearish"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"조건 미충족: Supertrend={direction}, RSI={rsi_val:.1f}",
            invalidation="",
        )
