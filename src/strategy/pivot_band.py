"""
PivotBand Strategy:
- 피벗 포인트 기반 동적 밴드 (여러 피벗 레벨의 중간 영역)
- BUY:  prev_close < band_lower AND curr_close >= band_lower (하단 밴드 복귀)
- SELL: prev_close > band_upper AND curr_close <= band_upper (상단 밴드 이탈)
- confidence: HIGH if curr_close < s2 or curr_close > r2 else MEDIUM
- 최소 5행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 5


class PivotBandStrategy(BaseStrategy):
    name = "pivot_band"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for PivotBand")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]

        # 이전봉 기준 피벗
        h = float(prev["high"])
        l = float(prev["low"])
        c = float(prev["close"])

        pivot = (h + l + c) / 3
        r1 = 2 * pivot - l
        s1 = 2 * pivot - h
        r2 = pivot + (h - l)
        s2 = pivot - (h - l)
        r3 = h + 2 * (pivot - l)
        s3 = l - 2 * (h - pivot)

        band_upper = (r1 + r2) / 2
        band_lower = (s1 + s2) / 2

        curr_close = float(curr["close"])
        prev_close = float(df.iloc[idx - 1]["close"])

        # NaN guard
        for val in (pivot, r1, s1, r2, s2, band_upper, band_lower):
            if val != val:  # isnan
                return self._hold(df, "NaN in pivot calculation")

        context = (
            f"close={curr_close:.4f} band_upper={band_upper:.4f} "
            f"band_lower={band_lower:.4f} "
            f"r2={r2:.4f} s2={s2:.4f} r3={r3:.4f} s3={s3:.4f}"
        )

        # BUY: 하단 밴드 복귀
        if prev_close < band_lower and curr_close >= band_lower:
            conf = Confidence.HIGH if curr_close < s2 or curr_close > r2 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotBand lower band recovery: prev={prev_close:.4f} < band_lower={band_lower:.4f}, curr={curr_close:.4f} >= band_lower. {context}",
                invalidation=f"close < band_lower({band_lower:.4f}) 재이탈 시",
                bull_case=f"band_upper={band_upper:.4f} 회복 목표",
                bear_case=f"s2={s2:.4f} 하향 돌파 시 추가 하락",
            )

        # SELL: 상단 밴드 이탈
        if prev_close > band_upper and curr_close <= band_upper:
            conf = Confidence.HIGH if curr_close < s2 or curr_close > r2 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=curr_close,
                reasoning=f"PivotBand upper band rejection: prev={prev_close:.4f} > band_upper={band_upper:.4f}, curr={curr_close:.4f} <= band_upper. {context}",
                invalidation=f"close > band_upper({band_upper:.4f}) 재돌파 시",
                bull_case=f"r2={r2:.4f} 돌파 시 추가 상승",
                bear_case=f"band_lower={band_lower:.4f} 하락 목표",
            )

        return self._hold(df, f"No PivotBand signal: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
