"""
RelativeVolumeStrategy (Improved):
- RVOL = current_volume / avg_volume_20
- VWAP = 거래량 가중 이동 평균 (rolling 20)
- BUY: RVOL > 1.5 AND close > open AND (close > VWAP OR RVOL > 2.2)
- SELL: RVOL > 1.5 AND close < open AND (close < VWAP OR RVOL > 2.2)
- confidence: RVOL > 2.5 AND BB condition → HIGH, 그 외 MEDIUM
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_VOL_LOOKBACK = 20
_RVOL_BUY_SELL = 1.5
_RVOL_ALT = 2.2
_RVOL_HIGH_CONF = 2.5
_BB_WINDOW = 20
_BB_STD = 2.0


class RelativeVolumeStrategy(BaseStrategy):
    name = "relative_volume"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return self._hold_signal(0.0, "Insufficient data")

        idx = len(df) - 2
        last = df.iloc[idx]
        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])

        # RVOL: 신호 봉 직전 20봉 평균 (look-ahead 방지)
        vol_window = df["volume"].iloc[max(0, idx - _VOL_LOOKBACK):idx]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 1.0
        rvol = volume / avg_vol if avg_vol > 0 else 0.0

        # VWAP (rolling 20, 신호 봉 포함)
        cv = (df["close"] * df["volume"]).rolling(_VOL_LOOKBACK).sum()
        v = df["volume"].rolling(_VOL_LOOKBACK).sum()
        vwap_series = cv / v
        vwap = float(vwap_series.iloc[idx])

        # 볼린저 밴드 (신호 봉 포함 rolling 20)
        bb_mean = df["close"].rolling(_BB_WINDOW).mean()
        bb_std = df["close"].rolling(_BB_WINDOW).std()
        bb_upper = float(bb_mean.iloc[idx]) + _BB_STD * float(bb_std.iloc[idx])
        bb_lower = float(bb_mean.iloc[idx]) - _BB_STD * float(bb_std.iloc[idx])

        bull_candle = close > open_
        bear_candle = close < open_

        info = (
            f"rvol={rvol:.2f} close={close:.2f} open={open_:.2f} "
            f"vwap={vwap:.2f} bb_upper={bb_upper:.2f} bb_lower={bb_lower:.2f}"
        )

        # BUY: RVOL > 1.5 + 양봉 + (VWAP 돌파 OR 고RVOL > 2.2)
        if rvol > _RVOL_BUY_SELL and bull_candle and (close > vwap or rvol > _RVOL_ALT):
            high_conf = rvol > _RVOL_HIGH_CONF and close > bb_upper
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"RVOL 상승 돌파: {info}",
                invalidation=f"Close below VWAP ({vwap:.2f})",
                bull_case=info,
                bear_case=info,
            )

        # SELL: RVOL > 1.5 + 음봉 + (VWAP 이탈 OR 고RVOL > 2.2)
        if rvol > _RVOL_BUY_SELL and bear_candle and (close < vwap or rvol > _RVOL_ALT):
            high_conf = rvol > _RVOL_HIGH_CONF and close < bb_lower
            conf = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"RVOL 하락 이탈: {info}",
                invalidation=f"Close above VWAP ({vwap:.2f})",
                bull_case=info,
                bear_case=info,
            )

        return self._hold_signal(close, f"No signal (rvol={rvol:.2f}): {info}", info, info)

    def _hold_signal(self, entry_price: float, reason: str,
                     bull_case: str = "", bear_case: str = "") -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
