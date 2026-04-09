"""
ROC (Rate of Change) 전략:
- ROC = (close - close.shift(20)) / close.shift(20) * 100
- Signal = ROC의 9기간 EMA
- BUY: ROC > 0 AND ROC 상향 크로스 Signal
- SELL: ROC < 0 AND ROC 하향 크로스 Signal
- confidence: HIGH if |ROC| > 3.0, MEDIUM otherwise
- 최소 35행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_SIGNAL_PERIOD = 9
_MIN_ROWS = 35
_HIGH_CONF_THRESHOLD = 3.0


class ROCStrategy(BaseStrategy):
    name = "roc"

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

        roc = (df["close"] - df["close"].shift(_PERIOD)) / df["close"].shift(_PERIOD) * 100
        signal = roc.ewm(span=_SIGNAL_PERIOD, adjust=False).mean()

        roc_now = float(roc.iloc[idx])
        roc_prev = float(roc.iloc[idx - 1])
        sig_now = float(signal.iloc[idx])
        sig_prev = float(signal.iloc[idx - 1])

        entry = float(df["close"].iloc[idx])

        # BUY: ROC > 0 AND ROC 상향 크로스 Signal
        if roc_now > 0 and roc_prev <= sig_prev and roc_now > sig_now:
            conf = Confidence.HIGH if abs(roc_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ROC 상향 크로스: ROC {roc_prev:.2f} → {roc_now:.2f}, Signal {sig_now:.2f} (ROC > 0)",
                invalidation="ROC가 Signal 아래로 재하락 시",
                bull_case=f"ROC {roc_now:.2f} 양전, 상승 모멘텀 확인",
                bear_case="모멘텀 약화 시 되돌림 가능",
            )

        # SELL: ROC < 0 AND ROC 하향 크로스 Signal
        if roc_now < 0 and roc_prev >= sig_prev and roc_now < sig_now:
            conf = Confidence.HIGH if abs(roc_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ROC 하향 크로스: ROC {roc_prev:.2f} → {roc_now:.2f}, Signal {sig_now:.2f} (ROC < 0)",
                invalidation="ROC가 Signal 위로 재상승 시",
                bull_case="단순 조정일 수 있음",
                bear_case=f"ROC {roc_now:.2f} 음전, 하락 모멘텀 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"ROC 중립: ROC {roc_now:.2f}, Signal {sig_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
