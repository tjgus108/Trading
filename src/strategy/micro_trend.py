"""
MicroTrendStrategy: 단기(micro) 추세 감지.

- 최근 5봉의 고점/저점 HH-HL / LL-LH 패턴 분석
- BUY: hh_count >= 3 AND hl_count >= 3 AND slope > 0
- SELL: ll_count >= 3 AND lh_count >= 3 AND slope < 0
- confidence HIGH: hh_count == 4 AND hl_count == 4 (완벽한 4/4)
- 최소 행: 10
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class MicroTrendStrategy(BaseStrategy):
    name = "micro_trend"

    MIN_ROWS = 10

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return self._hold(df, "Insufficient data: minimum 10 rows required")

        idx = len(df) - 2
        last = self._last(df)
        close = float(last["close"])

        # 최근 5봉 (idx-4 ~ idx 포함)
        recent_highs = df["high"].iloc[idx - 4:idx + 1]
        recent_lows = df["low"].iloc[idx - 4:idx + 1]
        recent_closes = df["close"].iloc[idx - 4:idx + 1]

        # NaN 체크
        if recent_highs.isna().any() or recent_lows.isna().any() or recent_closes.isna().any():
            return self._hold(df, "Insufficient data: NaN in recent 5 bars")

        # HH-HL 패턴
        hh_count = sum(
            1 for i in range(1, len(recent_highs))
            if float(recent_highs.iloc[i]) > float(recent_highs.iloc[i - 1])
        )
        hl_count = sum(
            1 for i in range(1, len(recent_lows))
            if float(recent_lows.iloc[i]) > float(recent_lows.iloc[i - 1])
        )

        # LL-LH 패턴
        ll_count = sum(
            1 for i in range(1, len(recent_lows))
            if float(recent_lows.iloc[i]) < float(recent_lows.iloc[i - 1])
        )
        lh_count = sum(
            1 for i in range(1, len(recent_highs))
            if float(recent_highs.iloc[i]) < float(recent_highs.iloc[i - 1])
        )

        # 단기 기울기
        x = np.arange(5)
        slope = np.polyfit(x, recent_closes.values.astype(float), 1)[0]

        # Confidence
        if hh_count == 4 and hl_count == 4:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        reasoning_base = (
            f"hh={hh_count} hl={hl_count} ll={ll_count} lh={lh_count} slope={slope:.6f} close={close:.4f}"
        )

        # BUY: 완전한 HH-HL 추세
        if hh_count >= 3 and hl_count >= 3 and slope > 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MicroTrend BUY: HH-HL pattern confirmed. {reasoning_base}",
                invalidation=f"Break of recent low ({float(recent_lows.iloc[-1]):.4f})",
            )

        # SELL: 완전한 LL-LH 추세
        if ll_count >= 3 and lh_count >= 3 and slope < 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"MicroTrend SELL: LL-LH pattern confirmed. {reasoning_base}",
                invalidation=f"Break above recent high ({float(recent_highs.iloc[-1]):.4f})",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"MicroTrend HOLD: mixed pattern. {reasoning_base}",
            invalidation="",
        )

    def _hold(self, df: Optional[pd.DataFrame], reason: str) -> Signal:
        close = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
        )
