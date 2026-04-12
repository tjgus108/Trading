"""
Linear Regression Channel 전략 (linear_reg_channel):
- 30봉 선형 회귀 채널의 하단/상단 이탈 후 복귀 시 신호
- BUY:  prev_close < lower_1.5sig AND curr_close > lower_1.5sig (하단 이탈 후 복귀)
- SELL: prev_close > upper_1.5sig AND curr_close < upper_1.5sig (상단 이탈 후 복귀)
- confidence: HIGH if std_res > 0 AND |curr_close - reg_val_now| > 2*std_res else MEDIUM
- 최소 데이터: 35행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_N = 30


class LinearRegChannelStrategy(BaseStrategy):
    name = "linear_reg_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for LinearRegChannel (need 35 rows)")

        idx = len(df) - 2

        n = _N
        x = np.arange(n)
        y = df["close"].iloc[idx - n + 1: idx + 1].values.astype(float)

        slope, intercept = np.polyfit(x, y, 1)

        fitted = slope * x + intercept
        residuals = y - fitted
        std_res = float(residuals.std())

        reg_val_now = slope * (n - 1) + intercept
        reg_val_prev = slope * (n - 2) + intercept

        curr_close = float(df["close"].iloc[idx])
        prev_close = float(df["close"].iloc[idx - 1])

        upper_channel = reg_val_now + 2 * std_res
        lower_channel = reg_val_now - 2 * std_res

        # NaN check
        if any(v != v for v in (curr_close, prev_close, reg_val_now, std_res)):
            return self._hold(df, "LinearRegChannel: NaN in indicator values")

        # confidence
        if std_res > 0 and abs(curr_close - reg_val_now) > 2 * std_res:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        context = (
            f"close={curr_close:.2f} reg={reg_val_now:.2f} "
            f"upper={upper_channel:.2f} lower={lower_channel:.2f} "
            f"slope={slope:.6f} std={std_res:.4f}"
        )

        last = self._last(df)
        close_price = float(last["close"])

        # BUY: 하단 이탈 후 복귀
        buy_prev_threshold = reg_val_prev - 1.5 * std_res
        buy_curr_threshold = reg_val_now - 1.5 * std_res
        if prev_close < buy_prev_threshold and curr_close > buy_curr_threshold:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"LinearRegChannel BUY: 하단 채널 이탈 후 복귀 "
                    f"(prev={prev_close:.2f}<{buy_prev_threshold:.2f}, "
                    f"curr={curr_close:.2f}>{buy_curr_threshold:.2f})"
                ),
                invalidation="채널 하단 재이탈 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 상단 이탈 후 복귀
        sell_prev_threshold = reg_val_prev + 1.5 * std_res
        sell_curr_threshold = reg_val_now + 1.5 * std_res
        if prev_close > sell_prev_threshold and curr_close < sell_curr_threshold:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"LinearRegChannel SELL: 상단 채널 이탈 후 복귀 "
                    f"(prev={prev_close:.2f}>{sell_prev_threshold:.2f}, "
                    f"curr={curr_close:.2f}<{sell_curr_threshold:.2f})"
                ),
                invalidation="채널 상단 재이탈 시",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"LinearRegChannel HOLD: 채널 내부 ({context})", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        try:
            close_price = float(self._last(df)["close"])
        except Exception:
            close_price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
