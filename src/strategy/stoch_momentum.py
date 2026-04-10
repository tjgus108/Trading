"""
StochasticMomentumStrategy: SMI (Stochastic Momentum Index) 기반 전략.

로직:
- HighestHigh = high.rolling(13).max()
- LowestLow   = low.rolling(13).min()
- midpoint    = (HighestHigh + LowestLow) / 2
- distance    = close - midpoint
- HL_range    = HighestHigh - LowestLow
- SMI         = (distance.ewm(span=5).mean() / (HL_range/2).ewm(span=5).mean()) * 100
- SMI_signal  = SMI.ewm(span=3).mean()
- BUY : SMI crosses above SMI_signal AND SMI < 0
- SELL: SMI crosses below SMI_signal AND SMI > 0
- confidence : |SMI| >= 40 → HIGH, 그 외 → MEDIUM
- 최소 행: 20
"""

from typing import Tuple

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _calc_smi(df: pd.DataFrame) -> Tuple[float, float, float, float]:
    """
    (-2, -3) 봉의 SMI, SMI_signal 값 반환.
    Returns: (smi_cur, sig_cur, smi_prev, sig_prev)
    """
    work = df.iloc[:-1].copy()  # 진행 중 봉(-1) 제외

    high = work["high"]
    low = work["low"]
    close = work["close"]

    highest = high.rolling(13).max()
    lowest = low.rolling(13).min()
    midpoint = (highest + lowest) / 2
    distance = close - midpoint
    hl_range = highest - lowest

    dist_ema = distance.ewm(span=5, adjust=False).mean()
    range_ema = (hl_range / 2).ewm(span=5, adjust=False).mean()

    # 0 나누기 방지
    smi = dist_ema / range_ema.replace(0, float("nan")) * 100
    smi = smi.fillna(0.0)

    smi_signal = smi.ewm(span=3, adjust=False).mean()

    smi_cur = float(smi.iloc[-1])
    sig_cur = float(smi_signal.iloc[-1])
    smi_prev = float(smi.iloc[-2])
    sig_prev = float(smi_signal.iloc[-2])

    return smi_cur, sig_cur, smi_prev, sig_prev


class StochasticMomentumStrategy(BaseStrategy):
    name = "stoch_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        if "high" not in df.columns:
            df = df.copy()
            df["high"] = df["close"]
        if "low" not in df.columns:
            df = df.copy()
            df["low"] = df["close"]

        smi_cur, sig_cur, smi_prev, sig_prev = _calc_smi(df)
        last = self._last(df)
        close = float(last["close"])

        context = f"SMI={smi_cur:.2f} signal={sig_cur:.2f} close={close:.4f}"

        # BUY: SMI crosses above signal AND SMI < 0
        crossed_up = smi_prev <= sig_prev and smi_cur > sig_cur
        if crossed_up and smi_cur < 0:
            confidence = Confidence.HIGH if smi_cur < -40 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"SMI 과매도 상향 돌파: {context}",
                invalidation="SMI가 다시 signal 하향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL: SMI crosses below signal AND SMI > 0
        crossed_down = smi_prev >= sig_prev and smi_cur < sig_cur
        if crossed_down and smi_cur > 0:
            confidence = Confidence.HIGH if smi_cur > 40 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"SMI 과매수 하향 돌파: {context}",
                invalidation="SMI가 다시 signal 상향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}")

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
