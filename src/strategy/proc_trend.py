"""
PRoCTrendStrategy: Price Rate of Change + Trend Filter 복합 전략.

계산:
  PROC = (close - close.shift(10)) / close.shift(10) * 100  (10봉 변화율)
  PROC_EMA = EMA(PROC, 5)  (평활화)
  Trend = EMA50 기울기 (현재 EMA50 vs 5봉 전 EMA50)

BUY:
  PROC_EMA > 0, PROC_EMA 상승 중, EMA50 상승 중, PROC_EMA > 1.0

SELL:
  PROC_EMA < 0, PROC_EMA 하락 중, EMA50 하락 중, PROC_EMA < -1.0

confidence: HIGH if |PROC_EMA| > 3.0, MEDIUM otherwise
최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_HIGH_CONF_THRESHOLD = 3.0
_MIN_THRESHOLD = 1.0


class PRoCTrendStrategy(BaseStrategy):
    name = "proc_trend"

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

        proc = (df["close"] - df["close"].shift(10)) / df["close"].shift(10) * 100
        proc_ema = proc.ewm(span=5, adjust=False).mean()

        proc_now = float(proc_ema.iloc[idx])
        proc_prev = float(proc_ema.iloc[idx - 1])
        ema50_now = float(df["ema50"].iloc[idx])
        ema50_prev5 = float(df["ema50"].iloc[idx - 5])
        trend_up = ema50_now > ema50_prev5
        trend_down = ema50_now < ema50_prev5

        entry = float(df["close"].iloc[idx])

        # BUY
        if (
            proc_now > 0
            and proc_now > proc_prev
            and trend_up
            and proc_now > _MIN_THRESHOLD
        ):
            conf = Confidence.HIGH if abs(proc_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"PROC_EMA 상승 모멘텀: {proc_prev:.2f} → {proc_now:.2f}, "
                    f"EMA50 상승 ({ema50_prev5:.2f} → {ema50_now:.2f})"
                ),
                invalidation="PROC_EMA가 0 아래로 하락 시",
                bull_case=f"PROC_EMA {proc_now:.2f}, 상승 추세 확인",
                bear_case="모멘텀 약화 시 되돌림 가능",
            )

        # SELL
        if (
            proc_now < 0
            and proc_now < proc_prev
            and trend_down
            and proc_now < -_MIN_THRESHOLD
        ):
            conf = Confidence.HIGH if abs(proc_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"PROC_EMA 하락 모멘텀: {proc_prev:.2f} → {proc_now:.2f}, "
                    f"EMA50 하락 ({ema50_prev5:.2f} → {ema50_now:.2f})"
                ),
                invalidation="PROC_EMA가 0 위로 상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"PROC_EMA {proc_now:.2f}, 하락 추세 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"PROC_EMA 중립: {proc_now:.2f} (이전: {proc_prev:.2f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )
