"""
TrendStrengthIndexStrategy (TSI — True Strength Index):
- diff = close.diff()
- abs_diff = diff.abs()
- ema_diff = diff.ewm(span=25, adjust=False).mean()
- ema_ema_diff = ema_diff.ewm(span=13, adjust=False).mean()
- ema_abs = abs_diff.ewm(span=25, adjust=False).mean()
- ema_ema_abs = ema_abs.ewm(span=13, adjust=False).mean()
- tsi = 100 * ema_ema_diff / ema_ema_abs
- signal = tsi.ewm(span=7, adjust=False).mean()
- BUY:  tsi crosses above signal AND tsi < 0 (과매도 구간 크로스)
- SELL: tsi crosses below signal AND tsi > 0
- confidence: HIGH if abs(tsi) > 25 else MEDIUM
- 최소 데이터: 40행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40


class TrendStrengthIndexStrategy(BaseStrategy):
    name = "trend_strength_index"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: need {_MIN_ROWS} rows",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        diff = df["close"].diff()
        abs_diff = diff.abs()

        ema_diff = diff.ewm(span=25, adjust=False).mean()
        ema_ema_diff = ema_diff.ewm(span=13, adjust=False).mean()
        ema_abs = abs_diff.ewm(span=25, adjust=False).mean()
        ema_ema_abs = ema_abs.ewm(span=13, adjust=False).mean()

        tsi = 100 * ema_ema_diff / ema_ema_abs.replace(0, 1e-10)
        signal_line = tsi.ewm(span=7, adjust=False).mean()

        tsi_now = float(tsi.iloc[idx])
        sig_now = float(signal_line.iloc[idx])
        tsi_prev = float(tsi.iloc[idx - 1])
        sig_prev = float(signal_line.iloc[idx - 1])

        if pd.isna(tsi_now) or pd.isna(sig_now):
            close = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="TSI NaN — Insufficient data",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        close = float(df["close"].iloc[idx])

        cross_up = tsi_prev < sig_prev and tsi_now >= sig_now
        cross_down = tsi_prev > sig_prev and tsi_now <= sig_now

        # BUY: crosses above signal AND tsi < 0
        if cross_up and tsi_now < 0:
            conf = Confidence.HIGH if abs(tsi_now) > 25 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"TSI crossover above signal in oversold zone: TSI={tsi_now:.2f} > Signal={sig_now:.2f} (TSI < 0)",
                invalidation="TSI drops back below signal line",
                bull_case=f"TSI={tsi_now:.2f}, 과매도 구간 상향 크로스",
                bear_case="크로스 이후 재하락 가능",
            )

        # SELL: crosses below signal AND tsi > 0
        if cross_down and tsi_now > 0:
            conf = Confidence.HIGH if abs(tsi_now) > 25 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"TSI crossover below signal in overbought zone: TSI={tsi_now:.2f} < Signal={sig_now:.2f} (TSI > 0)",
                invalidation="TSI rises back above signal line",
                bull_case="하락 모멘텀 소진 후 반등 가능",
                bear_case=f"TSI={tsi_now:.2f}, 과매수 구간 하향 크로스",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"TSI={tsi_now:.2f}, Signal={sig_now:.2f} — 크로스 조건 미충족",
            invalidation="",
            bull_case="",
            bear_case="",
        )
