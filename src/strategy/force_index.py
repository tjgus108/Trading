"""
Force Index 전략:
- Raw Force = (close - prev_close) * volume
- FI13 = EMA(Raw Force, 13)  (중기 추세)
- FI2 = EMA(Raw Force, 2)    (단기 힘)
- BUY: FI13 상승 중 AND close > ema50
- SELL: FI13 하락 중 AND close < ema50
- Confidence: HIGH if |FI13| > median(|FI13|, 20봉), MEDIUM otherwise
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class ForceIndexStrategy(BaseStrategy):
    name = "force_index"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        raw_force = df["close"].diff() * df["volume"]
        fi13 = raw_force.ewm(span=13, adjust=False).mean()
        fi2 = raw_force.ewm(span=2, adjust=False).mean()

        fi13_now = float(fi13.iloc[idx])
        fi13_prev = float(fi13.iloc[idx - 1])
        fi2_now = float(fi2.iloc[idx])
        close_now = float(df["close"].iloc[idx])
        ema50_now = float(df["ema50"].iloc[idx])

        fi13_abs_window = fi13.abs().iloc[idx - 20: idx]
        median_fi = float(fi13_abs_window.median()) if len(fi13_abs_window) > 0 else 1.0

        conf = Confidence.HIGH if abs(fi13_now) > median_fi else Confidence.MEDIUM

        fi13_rising = fi13_now > fi13_prev
        fi13_falling = fi13_now < fi13_prev

        if fi13_rising and close_now > ema50_now:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"FI13 상승: FI13={fi13_now:.2f} > prev={fi13_prev:.2f}, FI2={fi2_now:.2f}, close={close_now:.2f} > ema50={ema50_now:.2f}",
                invalidation="FI13 하락 전환 또는 close < ema50",
                bull_case="중기 매수 힘 강화 중",
                bear_case="단기 반등에 그칠 수 있음",
            )

        if fi13_falling and close_now < ema50_now:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=f"FI13 하락: FI13={fi13_now:.2f} < prev={fi13_prev:.2f}, FI2={fi2_now:.2f}, close={close_now:.2f} < ema50={ema50_now:.2f}",
                invalidation="FI13 상승 전환 또는 close > ema50",
                bull_case="단기 반등일 수 있음",
                bear_case="중기 매도 힘 강화 중",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_now,
            reasoning=f"FI13 방향 불명확 또는 가격 조건 불충족: FI13={fi13_now:.2f}, close={close_now:.2f}, ema50={ema50_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
