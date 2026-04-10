"""
RangeBoundStrategy: Choppiness Index + Mean Reversion.

CI = 100 * log10(sum(TR, n) / (max(high,n) - min(low,n))) / log10(n)
n = 14

CI > 61.8 → 횡보 (range-bound)
CI < 38.2 → 추세 (trending)

BUY:  CI > 61.8 AND close < SMA20 - 1*std  (하단 터치)
SELL: CI > 61.8 AND close > SMA20 + 1*std  (상단 터치)
HOLD: CI <= 61.8 (추세장) 또는 밴드 터치 없음

confidence: CI > 70 → HIGH, 그 외 MEDIUM
최소 행: 20
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

PERIOD = 14
CHOP_THRESHOLD = 61.8
STRONG_CHOP = 70.0
MIN_ROWS = 20


def _compute_ci(df: pd.DataFrame, idx: int) -> float:
    high_s = df["high"].iloc[idx - PERIOD + 1: idx + 1]
    low_s = df["low"].iloc[idx - PERIOD + 1: idx + 1]
    close_s = df["close"].iloc[idx - PERIOD + 1: idx + 1]
    prev_close = df["close"].iloc[idx - PERIOD: idx]

    hl = high_s - low_s
    hpc = pd.Series(
        (high_s.values - prev_close.values).__abs__(), index=high_s.index
    )
    lpc = pd.Series(
        (low_s.values - prev_close.values).__abs__(), index=low_s.index
    )
    tr = pd.concat([hl, hpc, lpc], axis=1).max(axis=1)

    atr_sum = float(tr.sum())
    hl_range = float(high_s.max() - low_s.min())
    return 100.0 * np.log10(atr_sum / max(hl_range, 1e-10)) / np.log10(PERIOD)


class RangeBoundStrategy(BaseStrategy):
    name = "range_bound"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2  # _last = iloc[-2]
        close = float(df["close"].iloc[idx])

        # CI 계산
        ci = _compute_ci(df, idx)

        # SMA20 + 표준편차 밴드
        close_window = df["close"].iloc[idx - 19: idx + 1]  # 20봉
        sma20 = float(close_window.mean())
        std20 = float(close_window.std(ddof=1))
        upper = sma20 + std20
        lower = sma20 - std20

        confidence = Confidence.HIGH if ci > STRONG_CHOP else Confidence.MEDIUM

        bull_case = (
            f"CI={ci:.2f} > {CHOP_THRESHOLD} (횡보), "
            f"close={close:.4f} < lower_band={lower:.4f} (평균회귀 BUY)"
        )
        bear_case = (
            f"CI={ci:.2f} > {CHOP_THRESHOLD} (횡보), "
            f"close={close:.4f} > upper_band={upper:.4f} (평균회귀 SELL)"
        )

        if ci > CHOP_THRESHOLD:
            if close < lower:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"횡보장 하단 반전: CI={ci:.2f} > {CHOP_THRESHOLD}, "
                        f"close={close:.4f} < lower={lower:.4f} (SMA20={sma20:.4f} - 1std)"
                    ),
                    invalidation=f"CI < {CHOP_THRESHOLD} (추세 전환) 또는 close < {lower - std20:.4f}",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if close > upper:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"횡보장 상단 반전: CI={ci:.2f} > {CHOP_THRESHOLD}, "
                        f"close={close:.4f} > upper={upper:.4f} (SMA20={sma20:.4f} + 1std)"
                    ),
                    invalidation=f"CI < {CHOP_THRESHOLD} (추세 전환) 또는 close > {upper + std20:.4f}",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            # 횡보장이지만 밴드 미접촉
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"횡보장 감지(CI={ci:.2f}) 하나 밴드 미접촉 "
                    f"(close={close:.4f}, lower={lower:.4f}, upper={upper:.4f})"
                ),
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 추세장 (CI <= 61.8)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=f"추세장: CI={ci:.2f} <= {CHOP_THRESHOLD} (Range Bound 신호 없음)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
