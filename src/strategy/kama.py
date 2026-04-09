"""
KAMA (Kaufman Adaptive Moving Average) 전략.

지표:
  ER  = |close - close.shift(10)| / sum(|close - close.shift(1)|, 10)
  fast_alpha = 2/(2+1)
  slow_alpha = 2/(30+1)
  SC  = (ER * (fast_alpha - slow_alpha) + slow_alpha)^2
  KAMA[i] = KAMA[i-1] + SC[i] * (close[i] - KAMA[i-1])

BUY:  이전봉 close < KAMA AND 현재봉 close > KAMA (상향 돌파)
SELL: 이전봉 close > KAMA AND 현재봉 close < KAMA (하향 돌파)
confidence: HIGH if 이격률 > 1%, MEDIUM 그 외
최소 데이터: 20행
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_FAST_ALPHA = 2.0 / (2 + 1)
_SLOW_ALPHA = 2.0 / (30 + 1)
_ER_PERIOD = 10
_MIN_ROWS = 20


def _compute_kama(close: pd.Series) -> pd.Series:
    """KAMA 시리즈 계산."""
    kama = close.copy().astype(float)
    n = len(close)

    for i in range(_ER_PERIOD, n):
        direction = abs(close.iloc[i] - close.iloc[i - _ER_PERIOD])
        volatility = (close.iloc[i - _ER_PERIOD + 1 : i + 1].diff().abs()).sum()
        er = direction / volatility if volatility != 0 else 0.0
        sc = (er * (_FAST_ALPHA - _SLOW_ALPHA) + _SLOW_ALPHA) ** 2
        kama.iloc[i] = kama.iloc[i - 1] + sc * (close.iloc[i] - kama.iloc[i - 1])

    # 첫 _ER_PERIOD 개 행은 close 값으로 채워지므로 NaN 처리
    kama.iloc[:_ER_PERIOD] = np.nan
    return kama


class KAMAStrategy(BaseStrategy):
    name = "kama"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-1]) if len(df) > 0 else 0.0,
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="",
            )

        kama_series = _compute_kama(df["close"])

        # _last(df) = df.iloc[-2] 패턴
        last = self._last(df)
        prev = df.iloc[-3]

        last_close = float(last["close"])
        prev_close = float(prev["close"])
        last_kama = float(kama_series.iloc[-2])
        prev_kama = float(kama_series.iloc[-3])

        if np.isnan(last_kama) or np.isnan(prev_kama):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="KAMA 계산 불가 (데이터 부족).",
                invalidation="",
            )

        gap_pct = abs(last_close - last_kama) / last_kama * 100 if last_kama != 0 else 0.0
        confidence = Confidence.HIGH if gap_pct > 1.0 else Confidence.MEDIUM

        crossed_up = prev_close < prev_kama and last_close > last_kama
        crossed_down = prev_close > prev_kama and last_close < last_kama

        if crossed_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"Close가 KAMA를 상향 돌파. close={last_close:.4f}, "
                    f"KAMA={last_kama:.4f}, 이격={gap_pct:.2f}%"
                ),
                invalidation=f"Close가 KAMA({last_kama:.4f}) 아래로 재진입 시 무효.",
                bull_case=f"KAMA 상향 돌파: 모멘텀 가속 구간.",
                bear_case="단기 되돌림 가능성.",
            )

        if crossed_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=last_close,
                reasoning=(
                    f"Close가 KAMA를 하향 돌파. close={last_close:.4f}, "
                    f"KAMA={last_kama:.4f}, 이격={gap_pct:.2f}%"
                ),
                invalidation=f"Close가 KAMA({last_kama:.4f}) 위로 재진입 시 무효.",
                bull_case="단기 반등 가능성.",
                bear_case=f"KAMA 하향 돌파: 하락 모멘텀 확인.",
            )

        position = "above" if last_close > last_kama else "below"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=last_close,
            reasoning=(
                f"KAMA 돌파 없음. close={last_close:.4f} {position} KAMA={last_kama:.4f}"
            ),
            invalidation="",
        )
