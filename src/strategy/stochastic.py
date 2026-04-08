"""
Stochastic Oscillator 전략:
- %K = (close - lowest_low_14) / (highest_high_14 - lowest_low_14) * 100
- %D = %K의 3봉 SMA
- BUY:  %K < 20 AND %D < 20 AND %K > %D (골든크로스 in 과매도)
- SELL: %K > 80 AND %D > 80 AND %K < %D (데드크로스 in 과매수)
- confidence: HIGH(%K<10 or %K>90), MEDIUM(%K<20 or %K>80)
- 최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_K_PERIOD = 14
_D_PERIOD = 3
_OVERSOLD = 20.0
_OVERBOUGHT = 80.0
_HIGH_CONF_LOW = 10.0
_HIGH_CONF_HIGH = 90.0


def _calc_stochastic(df: pd.DataFrame) -> "tuple[float, float]":
    """마지막 완성 캔들(-2) 기준 %K, %D 계산."""
    # 최근 _K_PERIOD + _D_PERIOD - 1 봉만 사용 (신호 봉 -2 포함)
    # -1 은 현재 진행 중 캔들 제외
    window = df.iloc[:-1]  # 진행 중 캔들 제외
    closes = window["close"]
    highs = window["high"]
    lows = window["low"]

    # %K 시리즈 계산
    k_series = []
    for i in range(_K_PERIOD - 1, len(window)):
        h = float(highs.iloc[i - _K_PERIOD + 1 : i + 1].max())
        l = float(lows.iloc[i - _K_PERIOD + 1 : i + 1].min())
        c = float(closes.iloc[i])
        denom = h - l
        if denom == 0:
            k_series.append(50.0)
        else:
            k_series.append((c - l) / denom * 100)

    if len(k_series) < _D_PERIOD:
        return 50.0, 50.0

    k_val = k_series[-1]
    d_val = sum(k_series[-_D_PERIOD:]) / _D_PERIOD
    return k_val, d_val


class StochasticStrategy(BaseStrategy):
    name = "stochastic"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        # high/low 컬럼이 없으면 close로 대체 (호환성)
        if "high" not in df.columns:
            df = df.copy()
            df["high"] = df["close"]
        if "low" not in df.columns:
            df = df.copy()
            df["low"] = df["close"]

        k, d = _calc_stochastic(df)
        last = self._last(df)
        close = float(last["close"])

        context = f"%K={k:.1f} %D={d:.1f} close={close:.4f}"

        # BUY: 과매도 + 골든크로스
        if k < _OVERSOLD and d < _OVERSOLD and k > d:
            confidence = Confidence.HIGH if k < _HIGH_CONF_LOW else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Stochastic 과매도 골든크로스: {context}",
                invalidation=f"%K 다시 %D 하향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 과매수 + 데드크로스
        if k > _OVERBOUGHT and d > _OVERBOUGHT and k < d:
            confidence = Confidence.HIGH if k > _HIGH_CONF_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Stochastic 과매수 데드크로스: {context}",
                invalidation=f"%K 다시 %D 상향 돌파 시",
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
