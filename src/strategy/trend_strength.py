"""
Trend Strength Index (TSI Bull) 전략:
- directional_move = close - close.shift(1)
- positive_dm = directional_move.clip(lower=0)
- negative_dm = (-directional_move).clip(lower=0)
- tsi_bull = positive_dm.rolling(10).sum() / (positive_dm.rolling(10).sum() + negative_dm.rolling(10).sum())
- BUY:  tsi_bull > 0.65 AND close > EMA50
- SELL: tsi_bull < 0.35 AND close < EMA50
- confidence: HIGH if tsi_bull > 0.75 or < 0.25, MEDIUM 그 외
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROLL = 10
_BUY_THRESH = 0.65
_SELL_THRESH = 0.35
_HIGH_BULL = 0.75
_HIGH_BEAR = 0.25


class TrendStrengthStrategy(BaseStrategy):
    name = "trend_strength"

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

        dm = df["close"].diff()
        pos_dm = dm.clip(lower=0)
        neg_dm = (-dm).clip(lower=0)

        pos_sum = pos_dm.rolling(_ROLL).sum()
        neg_sum = neg_dm.rolling(_ROLL).sum()
        total = pos_sum + neg_sum

        tsi_bull = pos_sum / total.replace(0, float("nan"))

        tsi_val = float(tsi_bull.iloc[idx])
        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        if pd.isna(tsi_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="TSI 계산 불가 (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        bull_case = (
            f"TSI_bull={tsi_val:.3f} > {_BUY_THRESH}, close={close:.4f} > EMA50={ema50:.4f}. "
            f"강한 상승 방향성."
        )
        bear_case = (
            f"TSI_bull={tsi_val:.3f} < {_SELL_THRESH}, close={close:.4f} < EMA50={ema50:.4f}. "
            f"강한 하락 방향성."
        )

        if tsi_val > _BUY_THRESH and close > ema50:
            conf = Confidence.HIGH if tsi_val > _HIGH_BULL else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"TSI_bull={tsi_val:.3f} > {_BUY_THRESH} AND close={close:.4f} > EMA50={ema50:.4f}"
                ),
                invalidation=f"TSI_bull < {_BUY_THRESH} 또는 close < EMA50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if tsi_val < _SELL_THRESH and close < ema50:
            conf = Confidence.HIGH if tsi_val < _HIGH_BEAR else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"TSI_bull={tsi_val:.3f} < {_SELL_THRESH} AND close={close:.4f} < EMA50={ema50:.4f}"
                ),
                invalidation=f"TSI_bull > {_SELL_THRESH} 또는 close > EMA50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"TSI_bull={tsi_val:.3f} (BUY>{_BUY_THRESH}, SELL<{_SELL_THRESH}), "
                f"close={close:.4f}, EMA50={ema50:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
