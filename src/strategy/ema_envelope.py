"""
EMAEnvelopeStrategy: EMA 기반 퍼센트 엔벨로프 전략.
- upper = ema20 * (1 + 2.5%)
- lower = ema20 * (1 - 2.5%)
- BUY: prev_close < lower AND curr_close > lower (하단 복귀)
- SELL: prev_close > upper AND curr_close < upper (상단 이탈)
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class EMAEnvelopeStrategy(BaseStrategy):
    name = "ema_envelope"

    MIN_ROWS = 25
    PCT = 0.025

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, "Insufficient data for EMAEnvelope (need 25 rows)")

        close = df["close"]
        ema20 = close.ewm(span=20, adjust=False).mean()

        pct = self.PCT
        upper = ema20 * (1 + pct)
        lower = ema20 * (1 - pct)

        idx = len(df) - 2
        curr_close = float(close.iloc[idx])
        prev_close = float(close.iloc[idx - 1])
        curr_ema20 = float(ema20.iloc[idx])
        curr_upper = float(upper.iloc[idx])
        curr_lower = float(lower.iloc[idx])
        prev_upper = float(upper.iloc[idx - 1])
        prev_lower = float(lower.iloc[idx - 1])

        if pd.isna(curr_ema20) or pd.isna(curr_upper) or pd.isna(curr_lower):
            return self._hold(df, "Insufficient data for EMAEnvelope (NaN detected)")

        entry = curr_close

        buy_signal = prev_close < prev_lower and curr_close > curr_lower
        sell_signal = prev_close > prev_upper and curr_close < curr_upper

        if buy_signal:
            confidence = Confidence.HIGH if curr_close < curr_ema20 * 0.97 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Price returned above lower envelope: prev={prev_close:.4f} < lower={prev_lower:.4f}, "
                    f"curr={curr_close:.4f} > lower={curr_lower:.4f}"
                ),
                invalidation=f"Close below lower envelope ({curr_lower:.4f})",
                bull_case=f"EMA20={curr_ema20:.4f}, lower={curr_lower:.4f}, price bounced",
                bear_case=f"May retest lower band or break down",
            )

        if sell_signal:
            confidence = Confidence.HIGH if curr_close > curr_ema20 * 1.03 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Price fell below upper envelope: prev={prev_close:.4f} > upper={prev_upper:.4f}, "
                    f"curr={curr_close:.4f} < upper={curr_upper:.4f}"
                ),
                invalidation=f"Close above upper envelope ({curr_upper:.4f})",
                bull_case=f"May recover above upper band",
                bear_case=f"EMA20={curr_ema20:.4f}, upper={curr_upper:.4f}, price rejected",
            )

        return self._hold(
            df,
            f"No envelope signal: close={curr_close:.4f}, lower={curr_lower:.4f}, upper={curr_upper:.4f}",
        )

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
