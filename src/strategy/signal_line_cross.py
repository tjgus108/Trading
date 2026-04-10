"""
SignalLineCrossStrategy:
- 범용 시그널 라인 크로스오버
- fast_line=EMA(8), slow_line=EMA(21), signal=EMA(diff,9)
- BUY: diff crosses above signal AND diff < 0 (음수 구간 크로스)
- SELL: diff crosses below signal AND diff > 0 (양수 구간 크로스)
- confidence: HIGH if abs(diff) > close.rolling(20).std()*0.02 else MEDIUM
- 최소 데이터: 35행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35


class SignalLineCrossStrategy(BaseStrategy):
    name = "signal_line_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for signal_line_cross (need 35 rows)")

        close = df["close"]

        fast_line = close.ewm(span=8, adjust=False).mean()
        slow_line = close.ewm(span=21, adjust=False).mean()
        diff = fast_line - slow_line
        signal = diff.ewm(span=9, adjust=False).mean()
        prev_diff = diff.shift(1)
        prev_signal = signal.shift(1)

        std20 = close.rolling(20).std()

        idx = len(df) - 2
        d = diff.iloc[idx]
        s = signal.iloc[idx]
        pd_ = prev_diff.iloc[idx]
        ps = prev_signal.iloc[idx]
        entry = float(close.iloc[idx])
        std_val = std20.iloc[idx]

        # NaN check
        if pd.isna(d) or pd.isna(s) or pd.isna(pd_) or pd.isna(ps):
            return self._hold(df, "Insufficient data for signal_line_cross (NaN)")

        std_val = std_val if not pd.isna(std_val) else 0.0
        high_conf = abs(d) > std_val * 0.02

        context = f"diff={d:.4f} signal={s:.4f} prev_diff={pd_:.4f}"

        # BUY: diff crosses above signal AND diff < 0
        if pd_ < ps and d >= s and d < 0:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Signal line BUY cross: diff({d:.4f}) crossed above signal({s:.4f}), diff<0 (negative zone)",
                invalidation=f"diff drops back below signal",
                bull_case=context,
                bear_case=context,
            )

        # SELL: diff crosses below signal AND diff > 0
        if pd_ > ps and d <= s and d > 0:
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Signal line SELL cross: diff({d:.4f}) crossed below signal({s:.4f}), diff>0 (positive zone)",
                invalidation=f"diff rises back above signal",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No cross signal: diff={d:.4f} signal={s:.4f}", context, context)

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
