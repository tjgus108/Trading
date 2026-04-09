"""
Session High Low 전략:
최근 session_window봉(기본 20)의 최고/최저를 추적.
close가 session_high 근처(session_high * 0.995 이상)이면 BUY,
close가 session_low 근처(session_low * 1.005 이하)이면 SELL.
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal


class SessionHighLowStrategy(BaseStrategy):
    name = "session_high_low"

    def __init__(self, session_window: int = 20) -> None:
        self.session_window = session_window

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 25
        if len(df) < min_rows:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]),
                reasoning=f"데이터 부족: {len(df)} < {min_rows}",
                invalidation="",
            )

        session = df.iloc[-self.session_window - 1 : -1]
        session_high: float = float(session["high"].max())
        session_low: float = float(session["low"].min())

        last = self._last(df)
        close: float = float(last["close"])
        entry: float = close

        near_high_threshold: float = session_high * 0.995
        near_low_threshold: float = session_low * 1.005

        near_high_001: float = session_high * 0.999
        near_low_001: float = session_low * 1.001

        bull_case = (
            f"close({close:.4f}) >= session_high*0.995({near_high_threshold:.4f}), "
            f"session_high={session_high:.4f}"
        )
        bear_case = (
            f"close({close:.4f}) <= session_low*1.005({near_low_threshold:.4f}), "
            f"session_low={session_low:.4f}"
        )

        if close >= near_high_threshold:
            conf = Confidence.HIGH if close >= near_high_001 else Confidence.MEDIUM
            proximity: float = (session_high - close) / session_high if session_high != 0 else 0.0
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"session_high 근접 매수: close({close:.4f}) >= {near_high_threshold:.4f}, "
                    f"proximity={proximity*100:.3f}%"
                ),
                invalidation=f"close가 session_high*0.995({near_high_threshold:.4f}) 아래로 하락",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if close <= near_low_threshold:
            conf = Confidence.HIGH if close <= near_low_001 else Confidence.MEDIUM
            proximity = (close - session_low) / session_low if session_low != 0 else 0.0
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"session_low 근접 매도: close({close:.4f}) <= {near_low_threshold:.4f}, "
                    f"proximity={proximity*100:.3f}%"
                ),
                invalidation=f"close가 session_low*1.005({near_low_threshold:.4f}) 위로 상승",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"세션 레인지 중간: close({close:.4f}) in "
                f"[{near_low_threshold:.4f}, {near_high_threshold:.4f}]"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
