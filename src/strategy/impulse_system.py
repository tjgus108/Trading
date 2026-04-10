"""
ImpulseSystem 전략.

Elder's Impulse System: EMA slope + MACD histogram slope 기반.

  ema13 = close의 13기간 EWM
  ema_slope = ema13.diff()
  ema12 = close의 12기간 EWM
  ema26 = close의 26기간 EWM
  macd = ema12 - ema26
  macd_signal = macd의 9기간 EWM
  macd_hist = macd - macd_signal
  macd_hist_slope = macd_hist.diff()

BUY:  ema_slope > 0 AND macd_hist_slope > 0 (Green bar)
SELL: ema_slope < 0 AND macd_hist_slope < 0 (Red bar)

confidence:
  HIGH   if abs(ema_slope) > std(ema_slope, 20)
  MEDIUM 그 외

최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


class ImpulseSystemStrategy(BaseStrategy):
    name = "impulse_system"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for ImpulseSystem (need 30 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]

        close = df["close"]

        ema13 = close.ewm(span=13, adjust=False).mean()
        ema_slope = ema13.diff()

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - macd_signal
        macd_hist_slope = macd_hist.diff()

        es_now = float(ema_slope.iloc[idx])
        mhs_now = float(macd_hist_slope.iloc[idx])
        close_now = float(close.iloc[idx])

        # NaN 체크
        if pd.isna(es_now) or pd.isna(mhs_now):
            return self._hold(df, "NaN in indicators")

        # ema_slope 표준편차 (최대 20봉)
        window = ema_slope.iloc[max(0, idx - 19): idx + 1]
        es_std = float(window.std()) if len(window) > 1 else 0.0

        context = (
            f"close={close_now:.4f} ema_slope={es_now:.6f} "
            f"macd_hist_slope={mhs_now:.6f}"
        )

        # BUY: ema_slope > 0 AND macd_hist_slope > 0
        if es_now > 0 and mhs_now > 0:
            confidence = (
                Confidence.HIGH
                if es_std > 0 and abs(es_now) > es_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"ImpulseSystem BUY: EMA 상승 + MACD hist 상승 (Green bar) "
                    f"(ema_slope={es_now:.6f}, macd_hist_slope={mhs_now:.6f})"
                ),
                invalidation="ema_slope 또는 macd_hist_slope 음전환",
                bull_case=context,
                bear_case=context,
            )

        # SELL: ema_slope < 0 AND macd_hist_slope < 0
        if es_now < 0 and mhs_now < 0:
            confidence = (
                Confidence.HIGH
                if es_std > 0 and abs(es_now) > es_std
                else Confidence.MEDIUM
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"ImpulseSystem SELL: EMA 하락 + MACD hist 하락 (Red bar) "
                    f"(ema_slope={es_now:.6f}, macd_hist_slope={mhs_now:.6f})"
                ),
                invalidation="ema_slope 또는 macd_hist_slope 양전환",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: ema_slope={es_now:.6f} macd_hist_slope={mhs_now:.6f}",
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
