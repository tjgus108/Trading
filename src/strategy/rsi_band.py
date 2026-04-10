"""
RSIBandStrategy: 동적 과매수/과매도 임계값을 사용하는 RSI 밴드 전략.
- BUY:  rsi < dynamic_os AND rsi > prev_rsi (과매도 + RSI 반등)
- SELL: rsi > dynamic_ob AND rsi < prev_rsi (과매수 + RSI 하락)
- confidence: HIGH if extreme divergence else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _calc_rsi(close: pd.Series) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
    rsi = 100 - 100 / (1 + gain / (loss + 1e-10))
    return rsi


class RSIBandStrategy(BaseStrategy):
    name = "rsi_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        close = df["close"].iloc[: idx + 1]
        rsi = _calc_rsi(close)

        rsi_ma = rsi.rolling(20, min_periods=1).mean()
        rsi_std = rsi.rolling(20, min_periods=1).std(ddof=0)

        dynamic_ob = rsi_ma + rsi_std * 1.0
        dynamic_os = rsi_ma - rsi_std * 1.0

        rsi_val = float(rsi.iloc[-1])
        prev_rsi = float(rsi.iloc[-2]) if len(rsi) >= 2 else rsi_val
        ob_val = float(dynamic_ob.iloc[-1])
        os_val = float(dynamic_os.iloc[-1])
        std_val = float(rsi_std.iloc[-1])

        if pd.isna(rsi_val) or pd.isna(ob_val) or pd.isna(os_val):
            return self._hold(df, "NaN indicator")

        last = self._last(df)
        price = float(last["close"])

        if rsi_val < os_val and rsi_val > prev_rsi:
            extreme = not pd.isna(std_val) and rsi_val < (os_val - std_val * 0.5)
            confidence = Confidence.HIGH if extreme else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"RSI({rsi_val:.2f}) < dynamic_os({os_val:.2f}), rebounding",
                invalidation=f"RSI drops below {os_val - std_val:.2f}",
                bull_case="Oversold bounce with RSI turning up",
                bear_case="Continued downtrend",
            )

        if rsi_val > ob_val and rsi_val < prev_rsi:
            extreme = not pd.isna(std_val) and rsi_val > (ob_val + std_val * 0.5)
            confidence = Confidence.HIGH if extreme else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=price,
                reasoning=f"RSI({rsi_val:.2f}) > dynamic_ob({ob_val:.2f}), turning down",
                invalidation=f"RSI rises above {ob_val + std_val:.2f}",
                bull_case="Continued uptrend",
                bear_case="Overbought reversal with RSI turning down",
            )

        return self._hold(df, "No signal")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
