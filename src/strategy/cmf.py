"""
CMF (Chaikin Money Flow) 전략:
- BUY: CMF > 0.05 (자금 유입) AND close > ema50
- SELL: CMF < -0.05 (자금 유출) AND close < ema50
- Confidence: HIGH if |CMF| > 0.15, MEDIUM otherwise
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 25
_BUY_THRESH = 0.05
_SELL_THRESH = -0.05
_HIGH_CONF = 0.15


class CMFStrategy(BaseStrategy):
    name = "cmf"

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

        h = df["high"].iloc[idx - _PERIOD + 1: idx + 1]
        l = df["low"].iloc[idx - _PERIOD + 1: idx + 1]
        c = df["close"].iloc[idx - _PERIOD + 1: idx + 1]
        v = df["volume"].iloc[idx - _PERIOD + 1: idx + 1]

        hl_range = h - l
        mfm = ((c - l) - (h - c)) / hl_range.where(hl_range != 0, 1.0)
        cmf = float((mfm * v).sum() / v.sum())

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        conf = Confidence.HIGH if abs(cmf) > _HIGH_CONF else Confidence.MEDIUM

        if cmf > _BUY_THRESH and close > ema50:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"CMF 자금 유입: CMF={cmf:.4f} > {_BUY_THRESH}, close={close:.2f} > ema50={ema50:.2f}",
                invalidation=f"CMF < {_BUY_THRESH} 또는 close < ema50",
                bull_case=f"CMF={cmf:.4f}, 강한 자금 유입 신호",
                bear_case="단기 반등일 수 있음",
            )

        if cmf < _SELL_THRESH and close < ema50:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"CMF 자금 유출: CMF={cmf:.4f} < {_SELL_THRESH}, close={close:.2f} < ema50={ema50:.2f}",
                invalidation=f"CMF > {_SELL_THRESH} 또는 close > ema50",
                bull_case="단기 반등일 수 있음",
                bear_case=f"CMF={cmf:.4f}, 강한 자금 유출 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"CMF 중립: CMF={cmf:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
