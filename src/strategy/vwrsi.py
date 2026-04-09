"""
VolumeWeightedRSIStrategy - 거래량 가중 RSI.

- price_change = close.diff()
- up_vol   = volume * (price_change > 0).astype(float)
- down_vol = volume * (price_change < 0).astype(float)
- up_vol_avg   = up_vol.ewm(span=14).mean()
- down_vol_avg = down_vol.ewm(span=14).mean()
- VW_RS   = up_vol_avg / (down_vol_avg + 1e-10)
- VWRSI   = 100 - 100 / (1 + VW_RS)
- BUY:  prev VWRSI < 30 AND now VWRSI >= 30 (crosses above 30)
- SELL: prev VWRSI > 70 AND now VWRSI <= 70 (crosses below 70)
- confidence: VWRSI < 20 (BUY) or VWRSI > 80 (SELL) → HIGH, else MEDIUM
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_EWM_SPAN = 14


def _calc_vwrsi(close: pd.Series, volume: pd.Series) -> pd.Series:
    price_change = close.diff()
    up_vol = volume * (price_change > 0).astype(float)
    down_vol = volume * (price_change < 0).astype(float)
    up_vol_avg = up_vol.ewm(span=_EWM_SPAN, adjust=False).mean()
    down_vol_avg = down_vol.ewm(span=_EWM_SPAN, adjust=False).mean()
    vw_rs = up_vol_avg / (down_vol_avg + 1e-10)
    return 100 - 100 / (1 + vw_rs)


class VolumeWeightedRSIStrategy(BaseStrategy):
    name = "vwrsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족 (최소 20행 필요)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        close = df["close"]
        volume = df["volume"]

        vwrsi = _calc_vwrsi(close, volume)
        vw_now = float(vwrsi.iloc[idx])
        vw_prev = float(vwrsi.iloc[idx - 1])
        entry = float(close.iloc[idx])

        # BUY: crosses above 30 (prev < 30, now >= 30)
        if vw_prev < 30 and vw_now >= 30:
            conf = Confidence.HIGH if vw_prev < 20 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VWRSI 30 상향돌파: {vw_prev:.2f}→{vw_now:.2f}",
                invalidation="VWRSI가 다시 30 하향 시",
                bull_case=f"VWRSI={vw_now:.2f}, 과매도 탈출",
                bear_case="추가 하락 가능성 있음",
            )

        # SELL: crosses below 70 (prev > 70, now <= 70)
        if vw_prev > 70 and vw_now <= 70:
            conf = Confidence.HIGH if vw_prev > 80 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"VWRSI 70 하향돌파: {vw_prev:.2f}→{vw_now:.2f}",
                invalidation="VWRSI가 다시 70 상향 시",
                bull_case="단기 반등 가능",
                bear_case=f"VWRSI={vw_now:.2f}, 과매수 탈출",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"VWRSI 중립: {vw_now:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
