"""
VolumeOscillatorV2 전략:
- 거래량 오실레이터 + 가격 방향 필터
- fast_vol = volume.ewm(span=5).mean()
- slow_vol = volume.ewm(span=20).mean()
- vol_osc  = (fast_vol - slow_vol) / (slow_vol + 1e-10) * 100
- vol_osc_ma = vol_osc.rolling(5).mean()
- price_up = close > close.shift(1)
- BUY:  vol_osc > 0 AND vol_osc > vol_osc_ma AND price_up
- SELL: vol_osc > 0 AND vol_osc > vol_osc_ma AND NOT price_up
- confidence: HIGH if vol_osc > 20 else MEDIUM
- 최소 행: 20
"""

import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_VOL_OSC_HIGH = 20.0


class VolumeOscillatorV2Strategy(BaseStrategy):
    name = "volume_oscillator_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold(0.0, "데이터 부족", "", "")

        idx = len(df) - 2

        volume = df["volume"]
        close = df["close"]

        fast_vol = volume.ewm(span=5, adjust=False).mean()
        slow_vol = volume.ewm(span=20, adjust=False).mean()
        vol_osc = (fast_vol - slow_vol) / (slow_vol + 1e-10) * 100
        vol_osc_ma = vol_osc.rolling(5, min_periods=1).mean()
        price_up = close > close.shift(1)

        vo_now = float(vol_osc.iloc[idx])
        vo_ma_now = float(vol_osc_ma.iloc[idx])
        close_now = float(close.iloc[idx])
        pu_now = bool(price_up.iloc[idx])

        # NaN 체크
        if any(v != v for v in (vo_now, vo_ma_now, close_now)):
            return self._hold(close_now, "NaN 값 감지", "", "")

        bull_case = (
            f"vol_osc={vo_now:.2f}, vol_osc_ma={vo_ma_now:.2f}, "
            f"price_up={pu_now}, close={close_now:.4f}"
        )
        bear_case = bull_case

        if vo_now > 0 and vo_now > vo_ma_now:
            conf = Confidence.HIGH if vo_now > _VOL_OSC_HIGH else Confidence.MEDIUM

            if pu_now:
                return Signal(
                    action=Action.BUY,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=close_now,
                    reasoning=(
                        f"거래량 증가(vol_osc={vo_now:.2f}>{vo_ma_now:.2f}) + 가격 상승"
                    ),
                    invalidation=f"vol_osc 감소 또는 가격 반전",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=conf,
                    strategy=self.name,
                    entry_price=close_now,
                    reasoning=(
                        f"거래량 증가(vol_osc={vo_now:.2f}>{vo_ma_now:.2f}) + 가격 하락"
                    ),
                    invalidation=f"vol_osc 감소 또는 가격 반전",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        reason = (
            f"조건 미충족. vol_osc={vo_now:.2f}, vol_osc_ma={vo_ma_now:.2f}"
        )
        return self._hold(close_now, reason, bull_case, bear_case)

    def _hold(self, entry: float, reason: str, bull_case: str, bear_case: str) -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
