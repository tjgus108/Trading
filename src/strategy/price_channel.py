"""
Price Channel Breakout 전략: 20봉 최고가/최저가 기반 단순화된 채널 돌파 전략.
RSI14 필터로 과매수/과매도 구간 진입 방지.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class PriceChannelStrategy(BaseStrategy):
    name = "price_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="Insufficient data (need at least 25 rows).",
                invalidation="",
            )

        idx = len(df) - 2
        period = 20

        high_slice = df["high"].iloc[idx - period: idx]
        low_slice = df["low"].iloc[idx - period: idx]
        upper = float(high_slice.max())
        lower = float(low_slice.min())
        middle = (upper + lower) / 2.0

        last = self._last(df)
        close = float(last["close"])
        rsi_val = float(_rsi(df["close"]).iloc[idx])

        if close > upper and rsi_val < 70:
            dist_pct = (close - upper) / upper
            conf = Confidence.HIGH if dist_pct > 0.01 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Channel breakout above Upper Channel ({upper:.4f}). "
                    f"Close={close:.4f}, RSI={rsi_val:.1f}, dist={dist_pct*100:.2f}%."
                ),
                invalidation=f"Close back below Upper Channel ({upper:.4f})",
                bull_case=f"Price broke above 20-bar Upper Channel ({upper:.4f}), RSI not overbought.",
                bear_case=f"False breakout risk. Middle={middle:.4f}, Lower={lower:.4f}.",
            )

        if close < lower and rsi_val > 30:
            dist_pct = (lower - close) / lower
            conf = Confidence.HIGH if dist_pct > 0.01 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Channel breakdown below Lower Channel ({lower:.4f}). "
                    f"Close={close:.4f}, RSI={rsi_val:.1f}, dist={dist_pct*100:.2f}%."
                ),
                invalidation=f"Close back above Lower Channel ({lower:.4f})",
                bull_case=f"Middle={middle:.4f}, Upper={upper:.4f}.",
                bear_case=f"Price broke below 20-bar Lower Channel ({lower:.4f}), RSI not oversold.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"No Price Channel breakout. "
                f"Close={close:.4f}, Upper={upper:.4f}, Lower={lower:.4f}, RSI={rsi_val:.1f}."
            ),
            invalidation="",
            bull_case=f"Upper Channel={upper:.4f}",
            bear_case=f"Lower Channel={lower:.4f}",
        )
