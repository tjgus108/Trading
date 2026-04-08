"""
Stochastic RSI 전략:
- RSI14 = 14기간 RSI (close 기반)
- StochRSI_K = (RSI - min(RSI,14)) / (max(RSI,14) - min(RSI,14)) * 100
- StochRSI_D = StochRSI_K의 3기간 SMA
- BUY:  K < 20 AND D < 20 AND K > D (상향 크로스 in 과매도)
- SELL: K > 80 AND D > 80 AND K < D (하향 크로스 in 과매수)
- confidence: HIGH(K<10 BUY / K>90 SELL), MEDIUM otherwise
- 최소 데이터: 35행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 35
_OVERSOLD = 20.0
_OVERBOUGHT = 80.0
_HIGH_CONF_LOW = 10.0
_HIGH_CONF_HIGH = 90.0


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class StochRSIStrategy(BaseStrategy):
    name = "stoch_rsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for StochRSI")

        idx = len(df) - 2  # _last() 패턴: 마지막 완성 캔들

        rsi = _rsi(df["close"], 14)
        rsi_min = rsi.rolling(14).min()
        rsi_max = rsi.rolling(14).max()
        stoch_k = 100 * (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, 1e-10)
        stoch_d = stoch_k.rolling(3).mean()

        k_now = float(stoch_k.iloc[idx])
        k_prev = float(stoch_k.iloc[idx - 1])
        d_now = float(stoch_d.iloc[idx])
        d_prev = float(stoch_d.iloc[idx - 1])

        last = self._last(df)
        close = float(last["close"])

        context = f"StochRSI K={k_now:.1f} D={d_now:.1f} close={close:.4f}"

        # BUY: 과매도 + K가 D 상향 크로스
        if k_now < _OVERSOLD and d_now < _OVERSOLD and k_now > d_now:
            confidence = Confidence.HIGH if k_now < _HIGH_CONF_LOW else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"StochRSI 과매도 상향 크로스: {context}",
                invalidation="StochRSI K가 D 하향 돌파 시",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 과매수 + K가 D 하향 크로스
        if k_now > _OVERBOUGHT and d_now > _OVERBOUGHT and k_now < d_now:
            confidence = Confidence.HIGH if k_now > _HIGH_CONF_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"StochRSI 과매수 하향 크로스: {context}",
                invalidation="StochRSI K가 D 상향 돌파 시",
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
