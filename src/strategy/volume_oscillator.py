"""
Volume Oscillator 전략:
- VO = (Short Vol EMA5 - Long Vol EMA20) / Long Vol EMA20 * 100
- BUY:  VO > 5 AND close > ema50
- SELL: VO > 5 AND close < ema50
- HOLD: VO <= 5
- confidence: HIGH if VO > 20, MEDIUM if VO > 5
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VO_THRESHOLD = 5.0
_VO_HIGH = 20.0


class VolumeOscillatorStrategy(BaseStrategy):
    name = "volume_oscillator"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2

        short_vol = df["volume"].ewm(span=5, adjust=False).mean()
        long_vol = df["volume"].ewm(span=20, adjust=False).mean()
        vo = (short_vol - long_vol) / long_vol.replace(0, 1e-10) * 100

        vo_now = float(vo.iloc[idx])
        close_now = float(df["close"].iloc[idx])
        ema50_now = float(df["ema50"].iloc[idx])

        bull_case = f"VO={vo_now:.2f} close={close_now:.2f} ema50={ema50_now:.2f}"
        bear_case = bull_case

        if vo_now > _VO_THRESHOLD:
            confidence = Confidence.HIGH if vo_now > _VO_HIGH else Confidence.MEDIUM

            if close_now > ema50_now:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_now,
                    reasoning=f"Volume surge (VO={vo_now:.2f}) + 상승추세 close({close_now:.2f})>ema50({ema50_now:.2f})",
                    invalidation=f"Close below EMA50 ({ema50_now:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

            if close_now < ema50_now:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close_now,
                    reasoning=f"Volume surge (VO={vo_now:.2f}) + 하락추세 close({close_now:.2f})<ema50({ema50_now:.2f})",
                    invalidation=f"Close above EMA50 ({ema50_now:.2f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        return self._hold(df, f"VO={vo_now:.2f} <= threshold({_VO_THRESHOLD})", bull_case, bear_case)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
