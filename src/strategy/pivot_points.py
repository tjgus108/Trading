"""
Pivot Points 기반 반전 전략:
- P  = (prev_high + prev_low + prev_close) / 3
- R1 = 2*P - prev_low    (1차 저항)
- S1 = 2*P - prev_high   (1차 지지)
- R2 = P + (prev_high - prev_low)  (2차 저항)
- S2 = P - (prev_high - prev_low)  (2차 지지)
- BUY:  close < S1 AND RSI14 < 40
- SELL: close > R1 AND RSI14 > 60
- 최소 5행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 5


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class PivotPointsStrategy(BaseStrategy):
    name = "pivot_points"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for Pivot Points")

        idx = len(df) - 2
        last = df.iloc[idx]
        prev = df.iloc[idx - 1]

        prev_high = float(prev["high"])
        prev_low = float(prev["low"])
        prev_close = float(prev["close"])
        close = float(last["close"])

        pivot = (prev_high + prev_low + prev_close) / 3
        r1 = 2 * pivot - prev_low
        s1 = 2 * pivot - prev_high
        r2 = pivot + (prev_high - prev_low)
        s2 = pivot - (prev_high - prev_low)

        rsi_val = float(_rsi(df["close"]).iloc[idx])

        context = (
            f"close={close:.4f} P={pivot:.4f} "
            f"S1={s1:.4f} S2={s2:.4f} R1={r1:.4f} R2={r2:.4f} "
            f"RSI={rsi_val:.1f}"
        )

        # BUY: close < S1 AND RSI < 40
        if close < s1 and rsi_val < 40:
            near_s2 = abs(close - s2) / max(abs(s2), 1e-10) < 0.005
            conf = Confidence.HIGH if near_s2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Pivot support 이탈: close < S1({s1:.4f}), "
                    f"RSI={rsi_val:.1f} 과매도. {context}"
                ),
                invalidation=f"close > S1({s1:.4f}) 회복 실패 시",
                bull_case=f"S2={s2:.4f} 지지 반등 기대",
                bear_case=f"S2={s2:.4f} 하향 돌파 시 추가 하락",
            )

        # SELL: close > R1 AND RSI > 60
        if close > r1 and rsi_val > 60:
            near_r2 = abs(close - r2) / max(abs(r2), 1e-10) < 0.005
            conf = Confidence.HIGH if near_r2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Pivot resistance 돌파: close > R1({r1:.4f}), "
                    f"RSI={rsi_val:.1f} 과매수. {context}"
                ),
                invalidation=f"close < R1({r1:.4f}) 재진입 시",
                bull_case=f"R2={r2:.4f} 돌파 시 추가 상승",
                bear_case=f"R2={r2:.4f} 저항 반락 기대",
            )

        return self._hold(df, f"No Pivot signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            last = self._last(df)
            price = float(last["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
