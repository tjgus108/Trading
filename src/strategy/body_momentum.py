"""
BodyMomentumStrategy: 캔들 몸통 크기 기반 모멘텀 전략.

- BM = body_ratio * direction  (-1 ~ +1)
- BM_EMA = EMA(BM, 10)
- BM_SUM = 최근 3봉 BM 합
- BUY:  BM_EMA > 0.3 AND BM_SUM > 0.5
- SELL: BM_EMA < -0.3 AND BM_SUM < -0.5
- confidence: HIGH if |BM_EMA| > 0.5, MEDIUM otherwise
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 20


class BodyMomentumStrategy(BaseStrategy):
    name = "body_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning="데이터 부족: BM 계산 불가",
                invalidation="",
            )

        idx = len(df) - 2

        body = (df["close"] - df["open"]).abs() / (df["high"] - df["low"] + 1e-10)
        direction = (df["close"] >= df["open"]).astype(float) * 2 - 1  # +1/-1
        bm = body * direction
        bm_ema = bm.ewm(span=10, adjust=False).mean()
        bm_sum3 = bm.rolling(3).sum()

        bm_ema_now = float(bm_ema.iloc[idx])
        bm_sum_now = float(bm_sum3.iloc[idx])
        close = float(df["close"].iloc[idx])

        bull_case = f"BM_EMA={bm_ema_now:.3f}, BM_SUM3={bm_sum_now:.3f}"
        bear_case = bull_case

        conf = (
            Confidence.HIGH
            if abs(bm_ema_now) > 0.5
            else Confidence.MEDIUM
        )

        # BUY: 연속 강한 양봉
        if bm_ema_now > 0.3 and bm_sum_now > 0.5:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"BM_EMA={bm_ema_now:.3f} > 0.3, "
                    f"BM_SUM3={bm_sum_now:.3f} > 0.5 (연속 강한 양봉)"
                ),
                invalidation="BM_EMA < 0.3 또는 BM_SUM3 < 0.5",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: 연속 강한 음봉
        if bm_ema_now < -0.3 and bm_sum_now < -0.5:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"BM_EMA={bm_ema_now:.3f} < -0.3, "
                    f"BM_SUM3={bm_sum_now:.3f} < -0.5 (연속 강한 음봉)"
                ),
                invalidation="BM_EMA > -0.3 또는 BM_SUM3 > -0.5",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"모멘텀 조건 미충족. BM_EMA={bm_ema_now:.3f}, "
                f"BM_SUM3={bm_sum_now:.3f}"
            ),
            invalidation="BM_EMA > 0.3 & BM_SUM3 > 0.5 (BUY) 또는 반대 (SELL)",
            bull_case=bull_case,
            bear_case=bear_case,
        )
