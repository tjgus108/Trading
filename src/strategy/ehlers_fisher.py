"""
EhlersFisherStrategy: Ehlers Fisher Transform 기반 전략.
가격을 정규분포로 변환하여 극단치 감지.
"""

import math
from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class EhlersFisherStrategy(BaseStrategy):
    name = "ehlers_fisher"

    def __init__(self, period: int = 10):
        self.period = period

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 15:
            return self._hold(df, "Insufficient data for EhlersFisher (need 15)")

        highest = df["high"].rolling(self.period).max()
        lowest = df["low"].rolling(self.period).min()

        hl_range = highest - lowest
        value = 2.0 * (df["close"] - lowest) / hl_range.replace(0, 0.0001) - 1.0
        value = value.clip(-0.999, 0.999)

        fish = pd.Series(
            [
                0.5 * math.log((1 + v) / (1 - v)) if -1 < v < 1 else 0.0
                for v in value
            ],
            index=df.index,
        )

        signal_line = fish.shift(1)

        idx = len(df) - 2

        if idx < 1:
            return self._hold(df, "Insufficient data for EhlersFisher (need 15)")

        # NaN check
        if pd.isna(fish.iloc[idx]) or pd.isna(signal_line.iloc[idx]):
            return self._hold(df, "EhlersFisher: NaN in indicators")

        curr_fish = float(fish.iloc[idx])
        prev_fish = float(fish.iloc[idx - 1])
        curr_sig = float(signal_line.iloc[idx])
        prev_sig = float(signal_line.iloc[idx - 1]) if not pd.isna(signal_line.iloc[idx - 1]) else curr_sig

        entry_price = float(df["close"].iloc[idx])

        abs_fish = abs(curr_fish)
        conf = Confidence.HIGH if abs_fish > 2.0 else Confidence.MEDIUM

        # BUY: fish crosses above signal AND fish < 0
        cross_up = prev_fish <= prev_sig and curr_fish > curr_sig
        if cross_up and curr_fish < 0:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EhlersFisher: 상향 크로스 (fish<0). "
                    f"fish={curr_fish:.3f} > signal={curr_sig:.3f}. "
                    f"|fish|={abs_fish:.3f} → {'HIGH' if abs_fish > 2.0 else 'MEDIUM'}."
                ),
                invalidation="fish 재하향 크로스 시 무효.",
                bull_case="Fisher 극단 저점 — 반등 기대.",
                bear_case="False cross 가능성 존재.",
            )

        # SELL: fish crosses below signal AND fish > 0
        cross_down = prev_fish >= prev_sig and curr_fish < curr_sig
        if cross_down and curr_fish > 0:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=(
                    f"EhlersFisher: 하향 크로스 (fish>0). "
                    f"fish={curr_fish:.3f} < signal={curr_sig:.3f}. "
                    f"|fish|={abs_fish:.3f} → {'HIGH' if abs_fish > 2.0 else 'MEDIUM'}."
                ),
                invalidation="fish 재상향 크로스 시 무효.",
                bull_case="False cross 가능성 존재.",
                bear_case="Fisher 극단 고점 — 하락 기대.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry_price,
            reasoning=(
                f"EhlersFisher: 크로스 없음. "
                f"fish={curr_fish:.3f}, signal={curr_sig:.3f}."
            ),
            invalidation="",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
        )
