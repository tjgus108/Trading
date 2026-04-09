"""
Volume Surge Breakout 전략:
- BUY: vol_ratio > 2.5 AND close > 20봉 고점(shift 1) AND 양봉
- SELL: vol_ratio > 2.5 AND close < 20봉 저점(shift 1) AND 음봉
- HOLD: 그 외
- confidence: HIGH(vol_ratio > 4.0), MEDIUM(> 2.5)
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_LOOKBACK = 20
_SURGE_MULT = 2.5
_HIGH_CONF_MULT = 4.0


class VolumeSurgeStrategy(BaseStrategy):
    name = "volume_surge"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])

        # vol_avg_20: 신호 봉 이전 20개 봉 평균 (look-ahead 방지)
        signal_idx = len(df) - 2
        vol_window = df["volume"].iloc[max(0, signal_idx - _VOL_LOOKBACK):signal_idx]
        vol_avg_20 = float(vol_window.mean()) if len(vol_window) > 0 else 1.0
        vol_ratio = volume / vol_avg_20 if vol_avg_20 > 0 else 0.0

        # 20봉 고점/저점 (shift 1 = 신호 봉 직전까지)
        prev_window = df["close"].iloc[max(0, signal_idx - _VOL_LOOKBACK):signal_idx]
        high_20 = float(prev_window.max())
        low_20 = float(prev_window.min())

        surge = vol_ratio > _SURGE_MULT
        bull_candle = close > open_
        bear_candle = close < open_
        above_high = close > high_20
        below_low = close < low_20

        info = (
            f"vol_ratio={vol_ratio:.2f} vol={volume:.0f} avg={vol_avg_20:.0f} "
            f"high20={high_20:.2f} low20={low_20:.2f} close={close:.2f}"
        )

        if surge and bull_candle and above_high:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume surge 상승 돌파: {info}",
                invalidation=f"Close below 20-bar high ({high_20:.2f})",
                bull_case=info,
                bear_case=info,
            )

        if surge and bear_candle and below_low:
            confidence = Confidence.HIGH if vol_ratio > _HIGH_CONF_MULT else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Volume surge 하락 붕괴: {info}",
                invalidation=f"Close above 20-bar low ({low_20:.2f})",
                bull_case=info,
                bear_case=info,
            )

        return self._hold(df, f"No signal: {info}", info, info)

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
