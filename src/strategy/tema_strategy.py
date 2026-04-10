"""
TEMAStrategy: Triple EMA(TEMA) 크로스오버 전략.

TEMA 계산: tema = 3*ema1 - 3*ema2 + ema3
- tema_fast (fast=10)
- tema_slow (slow=30)

BUY : tema_fast crosses above tema_slow
SELL: tema_fast crosses below tema_slow
HOLD: 그 외

confidence: HIGH if |tema_fast - tema_slow| / close > 0.015 else MEDIUM
최소 데이터: 40행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 40
_FAST = 10
_SLOW = 30
_HIGH_CONF_THRESHOLD = 0.015


def _tema(series: pd.Series, span: int) -> pd.Series:
    ema1 = series.ewm(span=span, adjust=False).mean()
    ema2 = ema1.ewm(span=span, adjust=False).mean()
    ema3 = ema2.ewm(span=span, adjust=False).mean()
    return 3 * ema1 - 3 * ema2 + ema3


class TEMAStrategy(BaseStrategy):
    name = "tema_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (최소 40행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]

        tema_fast = _tema(close, _FAST)
        tema_slow = _tema(close, _SLOW)

        tf_now = tema_fast.iloc[idx]
        tf_prev = tema_fast.iloc[idx - 1]
        ts_now = tema_slow.iloc[idx]
        ts_prev = tema_slow.iloc[idx - 1]
        price_now = close.iloc[idx]

        # NaN 체크
        if any(pd.isna(v) for v in [tf_now, tf_prev, ts_now, ts_prev, price_now]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (NaN 값 존재)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        entry = float(price_now)

        # confidence
        sep = abs(float(tf_now) - float(ts_now)) / float(price_now) if float(price_now) != 0 else 0.0
        conf = Confidence.HIGH if sep > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        # BUY: fast crosses above slow
        cross_up = float(tf_prev) < float(ts_prev) and float(tf_now) > float(ts_now)
        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"TEMA crossover BUY: tema_fast({tf_now:.4f}) > tema_slow({ts_now:.4f}) "
                    f"(이격 {sep*100:.3f}%)"
                ),
                invalidation="tema_fast가 tema_slow 아래로 하향 크로스 시",
                bull_case="TEMA 상향 크로스 — 단기 모멘텀 상승",
                bear_case="크로스가 fakeout일 수 있음",
            )

        # SELL: fast crosses below slow
        cross_down = float(tf_prev) > float(ts_prev) and float(tf_now) < float(ts_now)
        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"TEMA crossover SELL: tema_fast({tf_now:.4f}) < tema_slow({ts_now:.4f}) "
                    f"(이격 {sep*100:.3f}%)"
                ),
                invalidation="tema_fast가 tema_slow 위로 상향 크로스 시",
                bull_case="크로스가 fakeout일 수 있음",
                bear_case="TEMA 하향 크로스 — 단기 모멘텀 하락",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"TEMA 크로스 없음: tema_fast={tf_now:.4f}, tema_slow={ts_now:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
