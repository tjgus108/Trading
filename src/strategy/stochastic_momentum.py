"""
StochasticMomentumStrategy: SMI(Stochastic Momentum Index) 기반 전략.
- SMI = diff_smoothed / (range_smoothed + 1e-10) * 100  (-100 ~ +100)
- BUY:  smi < -40 AND smi > smi_signal (과매도 + 시그널 상향 크로스)
- SELL: smi >  40 AND smi < smi_signal (과매수 + 시그널 하향 크로스)
- confidence: HIGH if smi < -60 (BUY) or smi > 60 (SELL) else MEDIUM
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_LOOKBACK = 14
_OVERSOLD = -40.0
_OVERBOUGHT = 40.0
_HIGH_CONF_BUY = -60.0
_HIGH_CONF_SELL = 60.0


def _calc_smi(df: pd.DataFrame) -> "tuple[float, float]":
    """마지막 완성 캔들(-2) 기준 SMI, smi_signal 계산."""
    window = df.iloc[:-1]  # 진행 중 캔들 제외
    high = window["high"]
    low = window["low"]
    close = window["close"]

    highest_high = high.rolling(_LOOKBACK, min_periods=1).max()
    lowest_low = low.rolling(_LOOKBACK, min_periods=1).min()
    midpoint = (highest_high + lowest_low) / 2
    diff = close - midpoint
    diff_smoothed = diff.ewm(span=3, adjust=False).mean().ewm(span=3, adjust=False).mean()
    range_half = (highest_high - lowest_low) / 2
    range_smoothed = range_half.ewm(span=3, adjust=False).mean().ewm(span=3, adjust=False).mean()
    smi = diff_smoothed / (range_smoothed + 1e-10) * 100
    smi_signal = smi.ewm(span=10, adjust=False).mean()

    smi_val = float(smi.iloc[-1])
    signal_val = float(smi_signal.iloc[-1])
    return smi_val, signal_val


class StochasticMomentumStrategy(BaseStrategy):
    name = "stochastic_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        if "high" not in df.columns:
            df = df.copy()
            df["high"] = df["close"]
        if "low" not in df.columns:
            df = df.copy()
            df["low"] = df["close"]

        smi, smi_sig = _calc_smi(df)
        last = self._last(df)
        close = float(last["close"])

        import math
        if math.isnan(smi) or math.isnan(smi_sig):
            return self._hold(df, "NaN in SMI")

        context = f"SMI={smi:.1f} signal={smi_sig:.1f} close={close:.4f}"

        # BUY: 과매도 + 시그널 상향 크로스
        if smi < _OVERSOLD and smi > smi_sig:
            confidence = Confidence.HIGH if smi < _HIGH_CONF_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"SMI 과매도 + 시그널 상향 크로스 ({context})",
                invalidation=f"SMI {smi:.1f} → 0 이상으로 반전 시",
                bull_case="과매도 구간 반등 가능",
                bear_case="추세 하락 지속 시 손실",
            )

        # SELL: 과매수 + 시그널 하향 크로스
        if smi > _OVERBOUGHT and smi < smi_sig:
            confidence = Confidence.HIGH if smi > _HIGH_CONF_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"SMI 과매수 + 시그널 하향 크로스 ({context})",
                invalidation=f"SMI {smi:.1f} → 0 이하로 반전 시",
                bull_case="추세 상승 지속 시 손실",
                bear_case="과매수 구간 되돌림 가능",
            )

        return self._hold(df, context)

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        close = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="N/A",
        )
