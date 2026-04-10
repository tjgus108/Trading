"""
TrendlineBreakStrategy: 최근 20봉의 고점/저점 선형 회귀 추세선 돌파 전략.

- 상단 추세선: 고점들의 선형 회귀
- 하단 추세선: 저점들의 선형 회귀
- BUY: prev_close < trend_low_prev AND curr_close > trend_low_now
- SELL: prev_close > trend_high_prev AND curr_close < trend_high_now
- confidence: HIGH if slope_l > 0 (상승 추세선 돌파) for BUY, else MEDIUM
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class TrendlineBreakStrategy(BaseStrategy):
    name = "trendline_break"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < 25:
            return self._hold(df, "Insufficient data for trendline calculation (need 25+ rows)")

        idx = len(df) - 2
        n = 20
        x = np.arange(n)

        highs = df['high'].iloc[idx - n + 1:idx + 1].values.astype(float)
        lows = df['low'].iloc[idx - n + 1:idx + 1].values.astype(float)

        # NaN 체크
        if np.any(np.isnan(highs)) or np.any(np.isnan(lows)):
            return self._hold(df, "NaN values in high/low data")

        # 상단 추세선 (고점 회귀)
        slope_h, intercept_h = np.polyfit(x, highs, 1)
        trend_high_now = slope_h * (n - 1) + intercept_h
        trend_high_prev = slope_h * (n - 2) + intercept_h

        # 하단 추세선 (저점 회귀)
        slope_l, intercept_l = np.polyfit(x, lows, 1)
        trend_low_now = slope_l * (n - 1) + intercept_l
        trend_low_prev = slope_l * (n - 2) + intercept_l

        curr_close = float(df['close'].iloc[idx])
        prev_close = float(df['close'].iloc[idx - 1])

        entry = curr_close

        bull_case = (
            f"Close ({curr_close:.2f}) broke above lower trendline ({trend_low_now:.2f}). "
            f"slope_l={slope_l:.4f}"
        )
        bear_case = (
            f"Close ({curr_close:.2f}) broke below upper trendline ({trend_high_now:.2f}). "
            f"slope_h={slope_h:.4f}"
        )

        # BUY: 하단 추세선 상향 돌파
        if prev_close < trend_low_prev and curr_close > trend_low_now:
            conf = Confidence.HIGH if slope_l > 0 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Upward break of lower trendline. "
                    f"prev_close={prev_close:.2f} < trend_low_prev={trend_low_prev:.2f}, "
                    f"curr_close={curr_close:.2f} > trend_low_now={trend_low_now:.2f}. "
                    f"slope_l={slope_l:.4f}."
                ),
                invalidation=f"Close back below lower trendline ({trend_low_now:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 상단 추세선 하향 이탈
        if prev_close > trend_high_prev and curr_close < trend_high_now:
            conf = Confidence.HIGH if slope_h < 0 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Downward break of upper trendline. "
                    f"prev_close={prev_close:.2f} > trend_high_prev={trend_high_prev:.2f}, "
                    f"curr_close={curr_close:.2f} < trend_high_now={trend_high_now:.2f}. "
                    f"slope_h={slope_h:.4f}."
                ),
                invalidation=f"Close back above upper trendline ({trend_high_now:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"No trendline break. trend_low={trend_low_now:.2f}, trend_high={trend_high_now:.2f}, "
            f"close={curr_close:.2f}"
        )

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        if df is None or len(df) < 2:
            entry = 0.0
        else:
            entry = float(df['close'].iloc[-2])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
