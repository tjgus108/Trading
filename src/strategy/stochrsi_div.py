"""
StochRSI Divergence 전략:
  RSI14 = 14기간 RSI
  StochRSI = (RSI14 - min(RSI14, 14)) / (max(RSI14, 14) - min(RSI14, 14))
  %K = SMA(StochRSI, 3)
  %D = SMA(%K, 3)

과매도 반전 BUY:
  %K < 0.2 AND %K > %D (반전 시작) AND close > close.shift(1)

과매수 반전 SELL:
  %K > 0.8 AND %K < %D AND close < close.shift(1)

confidence: HIGH if |%K - 0.5| > 0.3, MEDIUM 그 외
최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal
from typing import Optional

_MIN_ROWS = 30
_OVERSOLD = 0.2
_OVERBOUGHT = 0.8
_HIGH_CONF_THRESHOLD = 0.3


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _calc_stochrsi_kd(close: pd.Series):
    """StochRSI %K, %D 계산. 반환값: (k, d) — 0~1 범위."""
    rsi = _rsi(close, 14)
    rsi_min = rsi.rolling(14).min()
    rsi_max = rsi.rolling(14).max()
    stoch = (rsi - rsi_min) / (rsi_max - rsi_min).replace(0, 1e-10)
    k = stoch.rolling(3).mean()
    d = k.rolling(3).mean()
    return k, d


class StochRSIDivStrategy(BaseStrategy):
    name = "stochrsi_div"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        k, d = _calc_stochrsi_kd(df["close"])

        idx = len(df) - 2  # _last() 패턴
        k_now = float(k.iloc[idx])
        d_now = float(d.iloc[idx])
        close_now = float(df["close"].iloc[idx])
        close_prev = float(df["close"].iloc[idx - 1])

        entry = close_now
        context = f"%K={k_now:.3f} %D={d_now:.3f} close={close_now:.4f}"

        confidence = (
            Confidence.HIGH if abs(k_now - 0.5) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
        )

        # BUY: 과매도 반전
        if k_now < _OVERSOLD and k_now > d_now and close_now > close_prev:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"StochRSI 과매도 반전: {context}",
                invalidation="%K가 %D 하향 돌파 또는 close 하락 시",
                bull_case=f"%K {k_now:.3f} < {_OVERSOLD} 과매도 구간, 반전 신호",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: 과매수 반전
        if k_now > _OVERBOUGHT and k_now < d_now and close_now < close_prev:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"StochRSI 과매수 반전: {context}",
                invalidation="%K가 %D 상향 돌파 또는 close 상승 시",
                bull_case="단기 조정일 수 있음",
                bear_case=f"%K {k_now:.3f} > {_OVERBOUGHT} 과매수 구간, 하락 반전",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"StochRSI 신호 없음: {context}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
