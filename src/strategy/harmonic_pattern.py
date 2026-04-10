"""
HarmonicPatternStrategy:
- 피보나치 비율 기반 간소화 ABCD 패턴
- A = close 20봉 전, B = 최근 10봉 최고, C = 최근 10봉 최저, D = 현재 close
- BUY: BC/AB 0.382~0.886 AND CD/BC 1.13~1.618 AND CD > 0
- SELL: BC/AB 0.382~0.886 AND CD/BC 1.13~1.618 AND CD < 0
- confidence: HIGH if BC/AB 0.618±0.02 else MEDIUM
- 최소 데이터: 20행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_RATIO_LOW = 0.382
_RATIO_HIGH = 0.886
_CD_LOW = 1.13
_CD_HIGH = 1.618
_GOLDEN = 0.618
_GOLDEN_TOL = 0.02


class HarmonicPatternStrategy(BaseStrategy):
    name = "harmonic_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        last = self._last(df)
        close = float(last["close"])

        completed = df.iloc[: idx + 1]

        if len(completed) < 20:
            return self._hold(df, "Insufficient completed candles for ABCD")

        a = float(completed["close"].iloc[-20])
        b = float(completed["close"].iloc[-10:].max())
        c = float(completed["close"].iloc[-10:].min())
        d = close

        ab = b - a
        bc = c - b
        cd = d - c

        if ab == 0 or bc == 0:
            return self._hold(df, "AB or BC == 0, cannot compute ratios")

        ratio_bc_ab = abs(bc) / abs(ab)
        ratio_cd_bc = abs(cd) / abs(bc)

        in_bc = _RATIO_LOW <= ratio_bc_ab <= _RATIO_HIGH
        in_cd = _CD_LOW <= ratio_cd_bc <= _CD_HIGH

        near_golden = abs(ratio_bc_ab - _GOLDEN) <= _GOLDEN_TOL
        confidence = Confidence.HIGH if near_golden else Confidence.MEDIUM

        context = (
            f"A={a:.4f} B={b:.4f} C={c:.4f} D={d:.4f} "
            f"BC/AB={ratio_bc_ab:.4f} CD/BC={ratio_cd_bc:.4f}"
        )

        if in_bc and in_cd:
            if cd > 0:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"Harmonic ABCD 상승 패턴: {context}",
                    invalidation=f"close < C={c:.4f}",
                    bull_case=f"CD > 0 상승 전환, BC/AB={ratio_bc_ab:.4f}",
                    bear_case="패턴 무효화 시 하락 지속",
                )
            elif cd < 0:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=f"Harmonic ABCD 하락 패턴: {context}",
                    invalidation=f"close > B={b:.4f}",
                    bull_case="패턴 무효화 시 상승 반전",
                    bear_case=f"CD < 0 하락 전환, BC/AB={ratio_bc_ab:.4f}",
                )

        return self._hold(df, f"No harmonic pattern: {context}")

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        if len(df) < 2:
            entry = 0.0
        else:
            last = self._last(df) if len(df) >= 2 else df.iloc[-1]
            entry = float(last["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
