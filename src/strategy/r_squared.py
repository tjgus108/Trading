"""
RSquaredStrategy: 선형 회귀 R² 기반 추세 강도 필터 전략.

- R² > 0.7 AND slope > 0 AND close > ema50 → BUY
- R² > 0.7 AND slope < 0 AND close < ema50 → SELL
- R² < 0.7 → HOLD (횡보장)
- confidence: HIGH if R² > 0.85, MEDIUM if R² > 0.7
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
PERIOD = 20


class RSquaredStrategy(BaseStrategy):
    name = "r_squared"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: R² 계산 불가",
                invalidation="",
            )

        idx = len(df) - 2
        y = df["close"].iloc[idx - PERIOD + 1: idx + 1].values.astype(float)
        x = np.arange(PERIOD, dtype=float)

        coeffs = np.polyfit(x, y, 1)
        slope = float(coeffs[0])
        fitted = np.polyval(coeffs, x)

        ss_res = float(np.sum((y - fitted) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r_sq = 1.0 - ss_res / max(ss_tot, 1e-10)

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        bull_case = f"R²={r_sq:.3f}, slope={slope:.4f}, close={close:.4f}, ema50={ema50:.4f}"
        bear_case = bull_case

        # HOLD: 횡보장
        if r_sq < 0.7:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning=f"R²={r_sq:.3f} < 0.7, 횡보장. slope={slope:.4f}",
                invalidation="R² > 0.7 돌파 시 추세 재확인",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        conf = Confidence.HIGH if r_sq > 0.85 else Confidence.MEDIUM

        # BUY: 강한 상승 추세
        if slope > 0 and close > ema50:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"R²={r_sq:.3f} > 0.7, slope={slope:.4f} > 0 (상승 추세), "
                    f"close={close:.4f} > ema50={ema50:.4f}"
                ),
                invalidation=f"close < ema50({ema50:.4f}) 또는 R² < 0.7",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 강한 하락 추세
        if slope < 0 and close < ema50:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"R²={r_sq:.3f} > 0.7, slope={slope:.4f} < 0 (하락 추세), "
                    f"close={close:.4f} < ema50={ema50:.4f}"
                ),
                invalidation=f"close > ema50({ema50:.4f}) 또는 R² < 0.7",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 추세 강하지만 ema50 방향 불일치 → HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"R²={r_sq:.3f} > 0.7, slope={slope:.4f}, "
                f"그러나 close vs ema50 방향 불일치"
            ),
            invalidation="slope 방향과 ema50 정렬 시 진입",
            bull_case=bull_case,
            bear_case=bear_case,
        )
