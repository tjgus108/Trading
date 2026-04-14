"""
SMI (Stochastic Momentum Index) 전략:
- SMI: 종가가 최근 고저 범위 중심에서 얼마나 떨어졌는지 측정
- 계산 (period=14, smooth=3):
  - HH = 14기간 최고가, LL = 14기간 최저가
  - Midpoint = (HH + LL) / 2
  - D = close - Midpoint
  - HL_range = HH - LL
  - SMI = 100 * EMA(EMA(D, 3), 3) / (0.5 * EMA(EMA(HL_range, 3), 3))
  - Signal = EMA(SMI, 3)
- BUY:  SMI < -40 (과매도) AND SMI > Signal (상승 중)
- SELL: SMI > 40  (과매수) AND SMI < Signal (하락 중)
- confidence: HIGH if SMI < -60 (BUY) or SMI > 60 (SELL), MEDIUM otherwise
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PERIOD = 14
_SMOOTH = 3
_OVERSOLD = -40.0
_OVERBOUGHT = 40.0
_HIGH_CONF_BUY = -60.0
_HIGH_CONF_SELL = 60.0


def _calc_smi(df: pd.DataFrame) -> "Tuple[float, float]":
    """idx = len(df) - 2 기준 SMI, Signal 계산."""
    period = _PERIOD
    smooth = _SMOOTH
    idx = len(df) - 2

    hh = df["high"].rolling(period).max()
    ll = df["low"].rolling(period).min()
    mid = (hh + ll) / 2
    d = df["close"] - mid
    hl = hh - ll

    smi = 100 * d.ewm(span=smooth, adjust=False).mean().ewm(span=smooth, adjust=False).mean() / \
          (0.5 * hl.ewm(span=smooth, adjust=False).mean().ewm(span=smooth, adjust=False).mean()).replace(0, 1e-10)
    signal = smi.ewm(span=smooth, adjust=False).mean()

    smi_now = float(smi.iloc[idx])
    sig_now = float(signal.iloc[idx])
    return smi_now, sig_now


class SMIStrategy(BaseStrategy):
    name = "smi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        smi_now, sig_now = _calc_smi(df)
        entry = float(df["close"].iloc[-2])

        is_buy = smi_now < _OVERSOLD and smi_now > sig_now
        is_sell = smi_now > _OVERBOUGHT and smi_now < sig_now

        if is_buy:
            confidence = Confidence.HIGH if smi_now < _HIGH_CONF_BUY else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SMI 과매도({smi_now:.1f}) + 상승 반전(Signal={sig_now:.1f})",
                invalidation=f"SMI {_OVERSOLD} 상향 유지 실패",
                bull_case=f"SMI={smi_now:.1f} < {_OVERSOLD}, Signal 상회",
                bear_case="모멘텀 반전 시 재하락 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if smi_now > _HIGH_CONF_SELL else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SMI 과매수({smi_now:.1f}) + 하락 반전(Signal={sig_now:.1f})",
                invalidation=f"SMI {_OVERBOUGHT} 하향 유지 실패",
                bull_case="과매수 해소 후 반등 가능",
                bear_case=f"SMI={smi_now:.1f} > {_OVERBOUGHT}, Signal 하회",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"SMI={smi_now:.1f}, Signal={sig_now:.1f} — 조건 미충족",
            invalidation="SMI 극단값 진입 시 재평가",
        )
