"""
RangeBiasStrategy:
- 봉의 위치 편향(Range Bias) — 거래 범위에서 종가의 위치 추세
- BUY:  bias > 0.6 AND bias_trend > 0 (위쪽 마감 편향 + 개선)
- SELL: bias < 0.4 AND bias_trend < 0 (아래쪽 마감 편향 + 악화)
- HOLD: 0.4 <= bias <= 0.6 또는 혼합
- confidence: HIGH if bias > 0.75 (BUY) or bias < 0.25 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class RangeBiasStrategy(BaseStrategy):
    name = "range_bias"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for range_bias (need 20 rows)")

        hl_range = df["high"] - df["low"]
        range_pos = (df["close"] - df["low"]) / hl_range.replace(0, 0.0001)

        bias = range_pos.rolling(5).mean()
        bias_ma = bias.rolling(10).mean()
        bias_trend = bias - bias_ma

        idx = len(df) - 2

        b = bias.iloc[idx]
        bt = bias_trend.iloc[idx]

        # NaN check
        if pd.isna(b) or pd.isna(bt):
            return self._hold(df, "Insufficient data for range_bias (NaN in indicators)")

        entry_price = float(df["close"].iloc[idx])
        context = f"bias={b:.4f} bias_trend={bt:.4f}"

        if b > 0.6 and bt > 0:
            confidence = Confidence.HIGH if b > 0.75 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"위쪽 마감 편향 + 개선: bias={b:.4f}>0.6, bias_trend={bt:.4f}>0",
                invalidation="bias < 0.6 or bias_trend < 0",
                bull_case=context,
                bear_case=context,
            )

        if b < 0.4 and bt < 0:
            confidence = Confidence.HIGH if b < 0.25 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=f"아래쪽 마감 편향 + 악화: bias={b:.4f}<0.4, bias_trend={bt:.4f}<0",
                invalidation="bias > 0.4 or bias_trend > 0",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: bias={b:.4f} bias_trend={bt:.4f}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
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
