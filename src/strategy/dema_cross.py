"""
DEMA Cross 전략: DEMA(5)가 DEMA(20)을 상향 돌파 시 BUY, 하향 돌파 시 SELL.

DEMA(n) = 2 * EMA(close, n) - EMA(EMA(close, n), n)
일반 EMA보다 노이즈가 적고 반응이 빠름.
최소 25행 필요.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


def _dema(series: pd.Series, period: int) -> pd.Series:
    ema = series.ewm(span=period, adjust=False).mean()
    ema_of_ema = ema.ewm(span=period, adjust=False).mean()
    return 2 * ema - ema_of_ema


class DEMACrossStrategy(BaseStrategy):
    name = "dema_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: 최소 25행 필요.",
                invalidation="",
            )

        idx = len(df) - 2
        dema5 = _dema(df["close"], 5)
        dema20 = _dema(df["close"], 20)

        d5_now = float(dema5.iloc[idx])
        d5_prev = float(dema5.iloc[idx - 1])
        d20_now = float(dema20.iloc[idx])
        d20_prev = float(dema20.iloc[idx - 1])

        cross_up = d5_prev <= d20_prev and d5_now > d20_now
        cross_down = d5_prev >= d20_prev and d5_now < d20_now

        dist_pct = abs(d5_now - d20_now) / max(abs(d20_now), 1e-10)
        conf = Confidence.HIGH if dist_pct > 0.005 else Confidence.MEDIUM

        entry = float(self._last(df)["close"])

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA5 ({d5_now:.4f}) crossed above DEMA20 ({d20_now:.4f}). "
                    f"이격률={dist_pct*100:.3f}%."
                ),
                invalidation=f"DEMA5가 DEMA20 ({d20_now:.4f}) 아래로 이탈 시",
                bull_case=f"DEMA5={d5_now:.4f} > DEMA20={d20_now:.4f}, 상향 크로스",
                bear_case=f"이전 DEMA5={d5_prev:.4f} ≤ DEMA20={d20_prev:.4f}",
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA5 ({d5_now:.4f}) crossed below DEMA20 ({d20_now:.4f}). "
                    f"이격률={dist_pct*100:.3f}%."
                ),
                invalidation=f"DEMA5가 DEMA20 ({d20_now:.4f}) 위로 회복 시",
                bull_case=f"이전 DEMA5={d5_prev:.4f} ≥ DEMA20={d20_prev:.4f}",
                bear_case=f"DEMA5={d5_now:.4f} < DEMA20={d20_now:.4f}, 하향 크로스",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"DEMA 크로스 없음. DEMA5={d5_now:.4f}, DEMA20={d20_now:.4f}, "
                f"이격률={dist_pct*100:.3f}%."
            ),
            invalidation="",
            bull_case=f"DEMA5={d5_now:.4f}, DEMA20={d20_now:.4f}",
            bear_case=f"DEMA5={d5_now:.4f}, DEMA20={d20_now:.4f}",
        )
