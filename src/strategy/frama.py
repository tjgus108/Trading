"""
FRAMA (Fractal Adaptive Moving Average) 전략.

alpha = exp(-4.6 * (D - 1))  (D = fractal dimension)
D = log(N1 + N2) - log(N) / log(2)
N1 = (max_high_half1 - min_low_half1) / (period/2)
N2 = (max_high_half2 - min_low_half2) / (period/2)
N  = (max_high_full - min_low_full) / period
period = 16 (기본값)
FRAMA[i] = alpha * close[i] + (1 - alpha) * FRAMA[i-1]

BUY:  close > FRAMA AND 이전봉 close < 이전봉 FRAMA (크로스)
SELL: close < FRAMA AND 이전봉 close > 이전봉 FRAMA
confidence: HIGH if 이격 > 1%, MEDIUM 그 외
최소 데이터: 35행
"""

import math
from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 35


def _compute_frama(closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, period: int = 16) -> np.ndarray:
    """FRAMA 배열 계산."""
    n = len(closes)
    frama = np.full(n, np.nan)

    half = period // 2

    # 초기값: 첫 번째 완성 구간의 마지막 close
    start = period - 1
    frama[start] = closes[start]

    for i in range(start + 1, n):
        # 현재 i 기준 이전 period 개 캔들 사용
        idx = i - period + 1
        h_full = highs[idx: i + 1]
        l_full = lows[idx: i + 1]

        h1 = highs[idx: idx + half]
        l1 = lows[idx: idx + half]
        h2 = highs[idx + half: i + 1]
        l2 = lows[idx + half: i + 1]

        max_h = h_full.max()
        min_l = l_full.min()
        max_h1 = h1.max()
        min_l1 = l1.min()
        max_h2 = h2.max()
        min_l2 = l2.min()

        N1 = (max_h1 - min_l1) / half
        N2 = (max_h2 - min_l2) / half
        N = (max_h - min_l) / period

        if N1 + N2 <= 0 or N <= 0:
            alpha = 0.01
        else:
            denom = math.log(2)
            if denom == 0:
                alpha = 0.01
            else:
                D = (math.log(N1 + N2) - math.log(N)) / denom
                D = max(1.0, min(2.0, D))
                alpha = math.exp(-4.6 * (D - 1.0))

        alpha = max(0.01, min(1.0, alpha))
        frama[i] = alpha * closes[i] + (1.0 - alpha) * frama[i - 1]

    return frama


class FRAMAStrategy(BaseStrategy):
    name = "frama"

    def __init__(self, period: int = 16) -> None:
        self.period = period

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: FRAMA 계산을 위해 최소 35행 필요",
                invalidation="",
            )

        closes = df["close"].values.astype(float)
        highs = df["high"].values.astype(float)
        lows = df["low"].values.astype(float)

        frama_arr = _compute_frama(closes, highs, lows, self.period)

        # -2: 마지막 완성 캔들, -3: 그 이전 캔들
        last_close = closes[-2]
        prev_close = closes[-3]
        last_frama = frama_arr[-2]
        prev_frama = frama_arr[-3]

        if np.isnan(last_frama) or np.isnan(prev_frama):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning="FRAMA 계산값 부족 (NaN)",
                invalidation="",
            )

        crossed_up = (prev_close < prev_frama) and (last_close > last_frama)
        crossed_down = (prev_close > prev_frama) and (last_close < last_frama)

        gap_pct = abs(last_close - last_frama) / last_frama * 100.0 if last_frama != 0 else 0.0
        confidence = Confidence.HIGH if gap_pct > 1.0 else Confidence.MEDIUM

        bull_case = f"close={last_close:.4f} > FRAMA={last_frama:.4f}, 이격={gap_pct:.2f}%"
        bear_case = f"close={last_close:.4f} < FRAMA={last_frama:.4f}, 이격={gap_pct:.2f}%"

        if crossed_up:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=f"FRAMA 상향 크로스. close={last_close:.4f} > FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%)",
                invalidation=f"Close below FRAMA ({last_frama:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if crossed_down:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=f"FRAMA 하향 크로스. close={last_close:.4f} < FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%)",
                invalidation=f"Close above FRAMA ({last_frama:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=float(last_close),
            reasoning=f"크로스 없음. close={last_close:.4f}, FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
