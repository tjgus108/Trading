"""
HighLowReversalStrategy:
- 고가/저가 대비 종가 위치(position) 반전 패턴
- BUY:  position < 0.2 AND position > pos_ma (저점 반등 시작)
- SELL: position > 0.8 AND position < pos_ma (고점 반락 시작)
- confidence: HIGH if position < 0.1 (BUY) or position > 0.9 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROLLING = 10
_BUY_THRESH = 0.2
_SELL_THRESH = 0.8
_HIGH_BUY = 0.1
_HIGH_SELL = 0.9


class HighLowReversalStrategy(BaseStrategy):
    name = "high_low_reversal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        hl_range = df["high"] - df["low"] + 1e-10
        position = (df["close"] - df["low"]) / hl_range
        pos_ma = position.rolling(_ROLLING, min_periods=1).mean()

        pos_val = float(position.iloc[idx])
        pos_ma_val = float(pos_ma.iloc[idx])

        if pd.isna(pos_val) or pd.isna(pos_ma_val):
            return self._hold(df, "NaN in position indicators")

        close = float(df["close"].iloc[idx])
        context = (
            f"close={close:.4f} position={pos_val:.4f} pos_ma={pos_ma_val:.4f}"
        )

        if pos_val < _BUY_THRESH and pos_val > pos_ma_val:
            confidence = Confidence.HIGH if pos_val < _HIGH_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"저점 반등 시작: position({pos_val:.4f})<{_BUY_THRESH} "
                    f"AND position>pos_ma({pos_ma_val:.4f})"
                ),
                invalidation=f"position drops below {pos_val:.4f} again",
                bull_case=context,
                bear_case=context,
            )

        if pos_val > _SELL_THRESH and pos_val < pos_ma_val:
            confidence = Confidence.HIGH if pos_val > _HIGH_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"고점 반락 시작: position({pos_val:.4f})>{_SELL_THRESH} "
                    f"AND position<pos_ma({pos_ma_val:.4f})"
                ),
                invalidation=f"position rises above {pos_val:.4f} again",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        idx = len(df) - 2
        close = float(df["close"].iloc[idx]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
