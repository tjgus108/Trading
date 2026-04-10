"""
AbsoluteStrengthHistStrategy — Absolute Strength Histogram (ASH).

- bulls/bears 강도를 이중 EWM 평활로 측정
- diff_val = smooth2_bulls - smooth2_bears

BUY:  diff_val crosses above 0 (이전 < 0, 현재 >= 0)
SELL: diff_val crosses below 0 (이전 > 0, 현재 <= 0)
HOLD: 그 외

confidence:
  HIGH   if abs(diff_val) > (smooth2_bulls + smooth2_bears) * 0.3
  MEDIUM otherwise

최소 데이터: 20행
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class AbsoluteStrengthHistStrategy(BaseStrategy):
    name = "absolute_strength_hist"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for AbsoluteStrengthHist (need 20 rows)")

        idx = len(df) - 2  # 마지막 완성 캔들

        diff = df["close"].diff()
        bulls = diff.clip(lower=0)
        bears = (-diff).clip(lower=0)

        smooth_bulls = bulls.ewm(span=9, adjust=False).mean()
        smooth_bears = bears.ewm(span=9, adjust=False).mean()

        smooth2_bulls = smooth_bulls.ewm(span=3, adjust=False).mean()
        smooth2_bears = smooth_bears.ewm(span=3, adjust=False).mean()

        diff_val_series = smooth2_bulls - smooth2_bears

        diff_now = float(diff_val_series.iloc[idx])
        diff_prev = float(diff_val_series.iloc[idx - 1])
        s2b_now = float(smooth2_bulls.iloc[idx])
        s2br_now = float(smooth2_bears.iloc[idx])
        close = float(df["close"].iloc[idx])

        total = s2b_now + s2br_now
        high_threshold = total * 0.3

        context = (
            f"close={close:.4f} diff_val={diff_now:.6f} "
            f"s2_bulls={s2b_now:.6f} s2_bears={s2br_now:.6f}"
        )

        # BUY: diff_val crosses above 0
        if diff_prev < 0 and diff_now >= 0:
            confidence = (
                Confidence.HIGH if abs(diff_now) > high_threshold else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ASH BUY: diff_val 0선 상향 돌파 "
                    f"({diff_prev:.6f} → {diff_now:.6f})"
                ),
                invalidation="diff_val 다시 0 하향 이탈",
                bull_case=context,
                bear_case=context,
            )

        # SELL: diff_val crosses below 0
        if diff_prev > 0 and diff_now <= 0:
            confidence = (
                Confidence.HIGH if abs(diff_now) > high_threshold else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ASH SELL: diff_val 0선 하향 이탈 "
                    f"({diff_prev:.6f} → {diff_now:.6f})"
                ),
                invalidation="diff_val 다시 0 상향 돌파",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No crossover: diff_prev={diff_prev:.6f} diff_now={diff_now:.6f}",
            context,
            context,
        )

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
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
