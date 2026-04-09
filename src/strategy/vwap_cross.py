"""
VWAP Crossover 전략:
- VWAP20과 VWAP50의 골든/데드 크로스로 방향성 포착
- BUY: VWAP20 상향 크로스 VWAP50
- SELL: VWAP20 하향 크로스 VWAP50
- confidence: HIGH if 이격률 > 0.5%, MEDIUM otherwise
- 최소 데이터: 55행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_HIGH_CONF_SPREAD = 0.005  # 0.5%


class VWAPCrossStrategy(BaseStrategy):
    name = "vwap_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        tp = (df["high"] + df["low"] + df["close"]) / 3
        vol = df["volume"]

        vwap20 = (tp * vol).rolling(20).sum() / vol.rolling(20).sum()
        vwap50 = (tp * vol).rolling(50).sum() / vol.rolling(50).sum()

        v20_now = float(vwap20.iloc[idx])
        v20_prev = float(vwap20.iloc[idx - 1])
        v50_now = float(vwap50.iloc[idx])
        v50_prev = float(vwap50.iloc[idx - 1])

        cross_up = v20_prev <= v50_prev and v20_now > v50_now
        cross_down = v20_prev >= v50_prev and v20_now < v50_now

        spread = abs(v20_now - v50_now) / (v50_now + 1e-10)
        confidence = Confidence.HIGH if spread > _HIGH_CONF_SPREAD else Confidence.MEDIUM

        close = float(df["close"].iloc[idx])

        bull_case = (
            f"VWAP20({v20_now:.4f}) > VWAP50({v50_now:.4f}), "
            f"spread={spread*100:.3f}%"
        )
        bear_case = (
            f"VWAP20({v20_now:.4f}) < VWAP50({v50_now:.4f}), "
            f"spread={spread*100:.3f}%"
        )

        if cross_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VWAP20 상향 크로스 VWAP50: "
                    f"prev({v20_prev:.4f}<={v50_prev:.4f}) → now({v20_now:.4f}>{v50_now:.4f}), "
                    f"spread={spread*100:.3f}%"
                ),
                invalidation=f"VWAP20 재하향 크로스 VWAP50 (현재 VWAP50={v50_now:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VWAP20 하향 크로스 VWAP50: "
                    f"prev({v20_prev:.4f}>={v50_prev:.4f}) → now({v20_now:.4f}<{v50_now:.4f}), "
                    f"spread={spread*100:.3f}%"
                ),
                invalidation=f"VWAP20 재상향 크로스 VWAP50 (현재 VWAP50={v50_now:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"No cross: VWAP20={v20_now:.4f} VWAP50={v50_now:.4f}",
            bull_case,
            bear_case,
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
