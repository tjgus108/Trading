"""
Mean Reversion Channel 전략.

- channel_mid   = SMA50
- channel_upper = SMA50 + 2 * std(close, 50)
- channel_lower = SMA50 - 2 * std(close, 50)
- z_score       = (close - SMA50) / std(close, 50)

BUY:  z_score < -2 AND z_score > 이전봉 z_score (반전 시작)
SELL: z_score > +2 AND z_score < 이전봉 z_score

confidence:
  HIGH   if |z_score| > 2.5
  MEDIUM if |z_score| > 2.0

최소 데이터: 55행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 55
_WINDOW = 50


class MeanReversionChannelStrategy(BaseStrategy):
    name = "mean_reversion_channel"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(
                df, "Insufficient data for Mean Reversion Channel (need 55 rows)"
            )

        idx = len(df) - 2  # _last() = iloc[-2]

        sma50 = df["close"].rolling(_WINDOW).mean()
        std50 = df["close"].rolling(_WINDOW).std()
        z_score = (df["close"] - sma50) / std50

        z_now = float(z_score.iloc[idx])
        z_prev = float(z_score.iloc[idx - 1])
        close = float(df["close"].iloc[idx])
        mid = float(sma50.iloc[idx])
        std_val = float(std50.iloc[idx])

        context = (
            f"close={close:.4f} sma50={mid:.4f} std={std_val:.4f} "
            f"z_score={z_now:.4f} z_prev={z_prev:.4f}"
        )

        # BUY: 과매도 반전
        if z_now < -2.0 and z_now > z_prev:
            confidence = (
                Confidence.HIGH if abs(z_now) > 2.5 else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"MeanReversionChannel BUY: z_score={z_now:.4f} < -2 "
                    f"및 반전 시작({z_prev:.4f}→{z_now:.4f})"
                ),
                invalidation="z_score 추가 하락 또는 -2 위로 회복 실패",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 과매수 반전
        if z_now > 2.0 and z_now < z_prev:
            confidence = (
                Confidence.HIGH if abs(z_now) > 2.5 else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"MeanReversionChannel SELL: z_score={z_now:.4f} > +2 "
                    f"및 반전 시작({z_prev:.4f}→{z_now:.4f})"
                ),
                invalidation="z_score 추가 상승 또는 +2 아래 회복 실패",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: z_score={z_now:.4f} (need <-2 or >+2 with reversal)",
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
