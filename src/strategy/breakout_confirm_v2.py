"""
BreakoutConfirmV2Strategy: 돌파 + 거래량 + 모멘텀 3단계 확인 전략.
기존 breakout_confirm.py와 다른 로직.
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class BreakoutConfirmV2Strategy(BaseStrategy):
    name = "breakout_confirm_v2"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < 25:
            price = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=price,
                reasoning="Insufficient data (need at least 25 rows).",
                invalidation="",
            )

        idx = len(df) - 2

        resistance = df["high"].rolling(20).max().shift(1)
        support = df["low"].rolling(20).min().shift(1)
        vol_ma20 = df["volume"].rolling(20).mean()

        close_val = float(df["close"].iloc[idx])
        res_val = float(resistance.iloc[idx])
        sup_val = float(support.iloc[idx])
        vol_val = float(df["volume"].iloc[idx])
        vol_ma_val = float(vol_ma20.iloc[idx])
        close_3ago = float(df["close"].iloc[idx - 3])

        if any(pd.isna(v) for v in [close_val, res_val, sup_val, vol_val, vol_ma_val, close_3ago]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val if not pd.isna(close_val) else 0.0,
                reasoning="NaN in indicator values.",
                invalidation="",
            )

        conf = Confidence.HIGH if vol_val > vol_ma_val * 2.0 else Confidence.MEDIUM

        vol_confirmed = vol_val > vol_ma_val * 1.3
        momentum_up = close_val > close_3ago
        momentum_down = close_val < close_3ago

        if close_val > res_val and vol_confirmed and momentum_up:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Breakout confirmed: close={close_val:.4f} > resistance={res_val:.4f}, "
                    f"volume={vol_val:.0f} > vol_ma20*1.3={vol_ma_val*1.3:.0f}, "
                    f"momentum up (close > close[3]={close_3ago:.4f})."
                ),
                invalidation=f"Close back below resistance ({res_val:.4f})",
                bull_case=f"Triple-confirmed breakout above {res_val:.4f} with strong volume.",
                bear_case=f"Risk of false breakout if volume fades.",
            )

        if close_val < sup_val and vol_confirmed and momentum_down:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"Breakdown confirmed: close={close_val:.4f} < support={sup_val:.4f}, "
                    f"volume={vol_val:.0f} > vol_ma20*1.3={vol_ma_val*1.3:.0f}, "
                    f"momentum down (close < close[3]={close_3ago:.4f})."
                ),
                invalidation=f"Close back above support ({sup_val:.4f})",
                bull_case=f"Support={sup_val:.4f}.",
                bear_case=f"Triple-confirmed breakdown below {sup_val:.4f} with strong volume.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_val,
            reasoning=(
                f"No confirmed breakout. close={close_val:.4f}, resistance={res_val:.4f}, "
                f"support={sup_val:.4f}, vol={vol_val:.0f}, vol_ma20={vol_ma_val:.0f}."
            ),
            invalidation="",
            bull_case=f"Resistance={res_val:.4f}",
            bear_case=f"Support={sup_val:.4f}",
        )
