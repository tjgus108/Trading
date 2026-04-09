"""
Choppiness Index 필터 전략.
시장이 추세인지 횡보인지 구분하여 추세장에서만 진입.

CI < 38.2 AND close > ema50 → BUY
CI < 38.2 AND close < ema50 → SELL
CI >= 38.2                  → HOLD (횡보장)

confidence: HIGH if CI < 30, MEDIUM if CI < 38.2
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

PERIOD = 14
TREND_THRESHOLD = 38.2
STRONG_TREND_THRESHOLD = 30.0
CHOP_THRESHOLD = 61.8


class ChoppinessStrategy(BaseStrategy):
    name = "choppiness"

    def generate(self, df: pd.DataFrame) -> Signal:
        min_rows = 20
        if len(df) < min_rows:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
            )

        idx = len(df) - 2
        entry = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        # CI 계산
        high_s = df["high"].iloc[idx - PERIOD + 1: idx + 1]
        low_s = df["low"].iloc[idx - PERIOD + 1: idx + 1]
        close_s = df["close"].iloc[idx - PERIOD + 1: idx + 1]
        prev_close = df["close"].iloc[idx - PERIOD: idx]

        tr_arr = pd.concat([
            high_s - low_s,
            (high_s - prev_close.values).abs(),
            (low_s - prev_close.values).abs()
        ], axis=1).max(axis=1)

        atr_sum = float(tr_arr.sum())
        hl_range = float(high_s.max() - low_s.min())
        ci = 100 * np.log10(atr_sum / max(hl_range, 1e-10)) / np.log10(PERIOD)

        bull_case = (
            f"CI={ci:.2f} < {TREND_THRESHOLD} (추세장), "
            f"close={entry:.4f} > ema50={ema50:.4f}"
        )
        bear_case = (
            f"CI={ci:.2f} < {TREND_THRESHOLD} (추세장), "
            f"close={entry:.4f} < ema50={ema50:.4f}"
        )

        if ci < TREND_THRESHOLD:
            confidence = Confidence.HIGH if ci < STRONG_TREND_THRESHOLD else Confidence.MEDIUM
            if entry > ema50:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"강한 추세장: CI={ci:.2f} < {TREND_THRESHOLD}. "
                        f"상승 추세: close={entry:.4f} > ema50={ema50:.4f}"
                    ),
                    invalidation=f"CI >= {TREND_THRESHOLD} 또는 close < ema50({ema50:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"강한 추세장: CI={ci:.2f} < {TREND_THRESHOLD}. "
                        f"하락 추세: close={entry:.4f} < ema50={ema50:.4f}"
                    ),
                    invalidation=f"CI >= {TREND_THRESHOLD} 또는 close > ema50({ema50:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        # CI >= 38.2 → 횡보
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"횡보장: CI={ci:.2f} >= {TREND_THRESHOLD} (추세 신호 없음)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
