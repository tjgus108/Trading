"""
VolumeROCStrategy: 거래량 변화율(Volume Rate of Change) 기반 전략.

로직:
- vol_roc     = (volume - volume.shift(10)) / volume.shift(10) * 100
- vol_roc_ema = vol_roc.ewm(span=5).mean()
- BUY : vol_roc_ema > 50 AND close > close.shift(1)
- SELL: vol_roc_ema > 50 AND close < close.shift(1)
- HOLD: vol_roc_ema < 20
- confidence : vol_roc_ema > 100 → HIGH, 그 외 → MEDIUM
- 최소 행: 15
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 15
_SIGNAL_THRESHOLD = 50.0
_HOLD_THRESHOLD = 20.0
_HIGH_CONF_THRESHOLD = 100.0


def _calc_vol_roc_ema(df: pd.DataFrame) -> float:
    """마지막 완성 캔들(-2) 기준 vol_roc_ema 반환."""
    work = df.iloc[:-1].copy()  # 진행 중 봉(-1) 제외
    volume = work["volume"]
    vol_roc = (volume - volume.shift(10)) / volume.shift(10) * 100
    vol_roc_ema = vol_roc.ewm(span=5, adjust=False).mean()
    return float(vol_roc_ema.iloc[-1])


class VolumeROCStrategy(BaseStrategy):
    name = "volume_roc"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])

        vol_roc_ema = _calc_vol_roc_ema(df)
        context = f"vol_roc_ema={vol_roc_ema:.2f} close={close:.4f}"

        # HOLD: 거래량 변화 미미
        if vol_roc_ema < _HOLD_THRESHOLD:
            return self._hold(df, f"Low volume ROC: {context}")

        confidence = Confidence.HIGH if vol_roc_ema > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM

        # 직전 봉 close (신호 봉 -2 기준 이전: -3)
        prev_close = float(df.iloc[-3]["close"])

        if vol_roc_ema > _SIGNAL_THRESHOLD:
            if close > prev_close:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"거래량 급증 + 상승: {context}",
                    invalidation="vol_roc_ema < 20 또는 가격 하락 전환 시",
                    bull_case=context,
                    bear_case=context,
                )
            elif close < prev_close:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"거래량 급증 + 하락: {context}",
                    invalidation="vol_roc_ema < 20 또는 가격 상승 전환 시",
                    bull_case=context,
                    bear_case=context,
                )

        return self._hold(df, f"No direction: {context}")

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
