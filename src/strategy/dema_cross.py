"""
DEMACrossStrategy: DEMA(fast=10)가 DEMA(slow=25)를 크로스할 때 신호 생성.

DEMA(n) = 2 * EMA(close, n) - EMA(EMA(close, n), n)
일반 EMA보다 노이즈가 적고 반응이 빠름.
최소 35행 필요.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


def _dema(series: pd.Series, period: int) -> pd.Series:
    ema = series.ewm(span=period, adjust=False).mean()
    ema_of_ema = ema.ewm(span=period, adjust=False).mean()
    return 2 * ema - ema_of_ema


class DEMACrossStrategy(BaseStrategy):
    name = "dema_cross"

    def __init__(self, fast: int = 10, slow: int = 25) -> None:
        self.fast = fast
        self.slow = slow

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < 35:
            close_val = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_val,
                reasoning="Insufficient data: minimum 35 rows required.",
                invalidation="",
            )

        idx = len(df) - 2
        dema_fast = _dema(df["close"], self.fast)
        dema_slow = _dema(df["close"], self.slow)

        df_now = float(dema_fast.iloc[idx])
        df_prev = float(dema_fast.iloc[idx - 1])
        ds_now = float(dema_slow.iloc[idx])
        ds_prev = float(dema_slow.iloc[idx - 1])

        if any(v != v for v in [df_now, df_prev, ds_now, ds_prev]):  # NaN check
            entry = float(self._last(df)["close"])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in DEMA values.",
                invalidation="",
            )

        cross_up = df_prev < ds_prev and df_now > ds_now
        cross_down = df_prev > ds_prev and df_now < ds_now

        close_price = float(df["close"].iloc[idx])
        dist_pct = abs(df_now - ds_now) / max(abs(close_price), 1e-10)
        conf = Confidence.HIGH if dist_pct > 0.01 else Confidence.MEDIUM

        entry = float(self._last(df)["close"])

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA_fast ({df_now:.4f}) crossed above DEMA_slow ({ds_now:.4f}). "
                    f"dist={dist_pct*100:.3f}%."
                ),
                invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 아래로 이탈 시",
                bull_case=f"DEMA_fast={df_now:.4f} > DEMA_slow={ds_now:.4f}, 상향 크로스",
                bear_case=f"이전 DEMA_fast={df_prev:.4f} < DEMA_slow={ds_prev:.4f}",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA_fast ({df_now:.4f}) crossed below DEMA_slow ({ds_now:.4f}). "
                    f"dist={dist_pct*100:.3f}%."
                ),
                invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 위로 회복 시",
                bull_case=f"이전 DEMA_fast={df_prev:.4f} > DEMA_slow={ds_prev:.4f}",
                bear_case=f"DEMA_fast={df_now:.4f} < DEMA_slow={ds_now:.4f}, 하향 크로스",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"DEMA 크로스 없음. DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}, "
                f"dist={dist_pct*100:.3f}%."
            ),
            invalidation="",
            bull_case=f"DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}",
            bear_case=f"DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}",
        )
