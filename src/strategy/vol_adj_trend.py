"""
VolAdjustedTrendStrategy: ATR14로 정규화된 가격 이동으로 추세 강도 측정.

- ATR14 = TR.ewm(span=14, adjust=False).mean()
- normalized_move = close.diff(5) / ATR14
- nm_ema = normalized_move.ewm(span=10, adjust=False).mean()
- BUY:  nm_ema > 1.5 AND nm_ema > nm_ema.shift(1) (가속 상승)
- SELL: nm_ema < -1.5 AND nm_ema < nm_ema.shift(1)
- confidence: nm_ema > 3.0 or nm_ema < -3.0 → HIGH
- 최소 행: 25
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class VolAdjustedTrendStrategy(BaseStrategy):
    name = "vol_adj_trend"

    def _compute(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        prev_close = close.shift(1)
        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr14 = tr.ewm(span=14, adjust=False).mean()
        normalized_move = close.diff(5) / atr14
        nm_ema = normalized_move.ewm(span=10, adjust=False).mean()

        result = df.copy()
        result["_atr14"] = atr14
        result["_nm_ema"] = nm_ema
        return result

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 25:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족: {len(df)} < 25",
                invalidation="",
            )

        computed = self._compute(df)
        nm_ema_series = computed["_nm_ema"]

        nm = float(nm_ema_series.iloc[-2])
        nm_prev = float(nm_ema_series.iloc[-3])
        entry = float(df["close"].iloc[-2])

        if pd.isna(nm) or pd.isna(nm_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 계산 중 NaN 발생.",
                invalidation="",
            )

        abs_nm = abs(nm)
        if abs_nm > 3.0:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        # BUY: nm_ema > 1.5 AND 가속 (nm > nm_prev)
        if nm > 1.5 and nm > nm_prev:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"nm_ema={nm:.3f} > 1.5, 가속 상승 (prev={nm_prev:.3f}).",
                invalidation="nm_ema가 1.5 하회 또는 감속 시 무효.",
                bull_case="ATR 대비 강한 상승 추세 가속 확인.",
                bear_case="추세 둔화 가능성 존재.",
            )

        # SELL: nm_ema < -1.5 AND 가속 (nm < nm_prev)
        if nm < -1.5 and nm < nm_prev:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"nm_ema={nm:.3f} < -1.5, 가속 하락 (prev={nm_prev:.3f}).",
                invalidation="nm_ema가 -1.5 상회 또는 감속 시 무효.",
                bull_case="추세 회복 가능성 존재.",
                bear_case="ATR 대비 강한 하락 추세 가속 확인.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"nm_ema={nm:.3f}. 조건 미충족.",
            invalidation="",
        )
