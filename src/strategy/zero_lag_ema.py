"""
ZeroLagEMAStrategy: Zero Lag EMA 크로스오버 전략.

zlema_fast (span=10) vs zlema_slow (span=25)
Zero-lag: zlema = 2*EMA - EMA(EMA)

BUY  : zlema_fast crosses above zlema_slow
SELL : zlema_fast crosses below zlema_slow
HOLD : 그 외
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


def _zlema_ec(close: pd.Series, span: int) -> pd.Series:
    ema = close.ewm(span=span, adjust=False).mean()
    ema_ema = ema.ewm(span=span, adjust=False).mean()
    return 2 * ema - ema_ema


class ZeroLagEMAStrategy(BaseStrategy):
    name = "zero_lag_ema"

    MIN_ROWS = 35
    SPAN_FAST = 10
    SPAN_SLOW = 25
    HIGH_CONF_THRESHOLD = 0.01  # 1%

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data (minimum {self.MIN_ROWS} rows required)",
                invalidation="N/A",
            )

        idx = len(df) - 2
        close = df["close"]

        zlema_fast = _zlema_ec(close, self.SPAN_FAST)
        zlema_slow = _zlema_ec(close, self.SPAN_SLOW)

        fast_now = float(zlema_fast.iloc[idx])
        fast_prev = float(zlema_fast.iloc[idx - 1])
        slow_now = float(zlema_slow.iloc[idx])
        slow_prev = float(zlema_slow.iloc[idx - 1])

        if any(pd.isna(v) for v in [fast_now, fast_prev, slow_now, slow_prev]):
            entry = float(close.iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in Zero Lag EMA",
                invalidation="N/A",
            )

        entry_price = float(close.iloc[idx])

        cross_up = fast_prev < slow_prev and fast_now > slow_now
        cross_down = fast_prev > slow_prev and fast_now < slow_now

        separation = abs(fast_now - slow_now) / entry_price if entry_price != 0 else 0.0
        confidence = Confidence.HIGH if separation > self.HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"ZeroLagEMA({self.SPAN_FAST})={fast_now:.4f} crossed above "
                    f"ZeroLagEMA({self.SPAN_SLOW})={slow_now:.4f} "
                    f"(separation={separation*100:.3f}%)"
                ),
                invalidation=f"ZeroLagEMA fast crosses below slow",
                bull_case="Zero-lag EMA 상향 크로스 — 지연 없는 모멘텀 상승",
                bear_case="fakeout 가능성",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"ZeroLagEMA({self.SPAN_FAST})={fast_now:.4f} crossed below "
                    f"ZeroLagEMA({self.SPAN_SLOW})={slow_now:.4f} "
                    f"(separation={separation*100:.3f}%)"
                ),
                invalidation=f"ZeroLagEMA fast crosses above slow",
                bull_case="fakeout 가능성",
                bear_case="Zero-lag EMA 하향 크로스 — 지연 없는 모멘텀 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"No cross — ZeroLagEMA({self.SPAN_FAST})={fast_now:.4f}, "
                f"ZeroLagEMA({self.SPAN_SLOW})={slow_now:.4f}"
            ),
            invalidation="크로스 발생 시 재평가",
        )
