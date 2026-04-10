"""
PricePatternRecogStrategy: 다중 캔들 패턴 인식
(Morning Star, Evening Star, Three White Soldiers, Three Black Crows)
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class PricePatternRecogStrategy(BaseStrategy):
    name = "price_pattern_recog"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 8:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data (minimum 8 rows required)",
                invalidation="N/A",
            )

        idx = len(df) - 2  # 마지막 완성 캔들

        # Require idx-3 for Three White/Black checks
        if idx < 3:
            entry = float(df["close"].iloc[-1])
            return self._hold(df, "Insufficient data (idx < 3)")

        o0 = float(df["open"].iloc[idx])
        h0 = float(df["high"].iloc[idx])
        l0 = float(df["low"].iloc[idx])
        c0 = float(df["close"].iloc[idx])

        o1 = float(df["open"].iloc[idx - 1])
        h1 = float(df["high"].iloc[idx - 1])
        l1 = float(df["low"].iloc[idx - 1])
        c1 = float(df["close"].iloc[idx - 1])

        o2 = float(df["open"].iloc[idx - 2])
        h2 = float(df["high"].iloc[idx - 2])
        l2 = float(df["low"].iloc[idx - 2])
        c2 = float(df["close"].iloc[idx - 2])

        c2_prev = float(df["close"].iloc[idx - 3])

        body2 = abs(c2 - o2)
        body1 = abs(c1 - o1)
        body0 = abs(c0 - o0)

        total_range2 = max(h2 - l2, 0.0001)
        range1 = max(h1 - l1, 0.0001)
        range0 = max(h0 - l0, 0.0001)

        entry = float(df["close"].iloc[idx])

        # Morning Star: 큰 음봉 + 작은 봉(도지) + 큰 양봉
        morning_star = (
            c2 < o2 and body2 / total_range2 > 0.5
            and body1 / range1 < 0.3
            and c0 > o0 and body0 / range0 > 0.5
            and c0 > (o2 + c2) / 2
        )

        # Evening Star: 큰 양봉 + 작은 봉 + 큰 음봉
        evening_star = (
            c2 > o2 and body2 / total_range2 > 0.5
            and body1 / range1 < 0.3
            and c0 < o0 and body0 / range0 > 0.5
            and c0 < (o2 + c2) / 2
        )

        # Three White Soldiers: 3연속 상승 강한 양봉
        three_white = (
            c2 > o2 and c1 > o1 and c0 > o0
            and c2 > c2_prev and c1 > c2 and c0 > c1
            and body2 > total_range2 * 0.5
            and body1 > range1 * 0.5
            and body0 > range0 * 0.5
        )

        # Three Black Crows: 3연속 하락 강한 음봉
        three_black = (
            c2 < o2 and c1 < o1 and c0 < o0
            and c2 < c2_prev and c1 < c2 and c0 < c1
            and body2 > total_range2 * 0.5
            and body1 > range1 * 0.5
            and body0 > range0 * 0.5
        )

        if morning_star or three_white:
            pattern = "Three White Soldiers" if three_white else "Morning Star"
            confidence = Confidence.HIGH if three_white else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"{pattern} 패턴 감지. BUY 신호.",
                invalidation=f"최근 저점 {min(l0, l1, l2):.4f} 하회 시 무효",
                bull_case="패턴이 상승 반전/지속 신호",
                bear_case="거래량 미동반 시 페이크아웃 가능",
            )

        if evening_star or three_black:
            pattern = "Three Black Crows" if three_black else "Evening Star"
            confidence = Confidence.HIGH if three_black else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"{pattern} 패턴 감지. SELL 신호.",
                invalidation=f"최근 고점 {max(h0, h1, h2):.4f} 상회 시 무효",
                bull_case="지지선 도달 시 반등 가능",
                bear_case="패턴이 하락 반전/지속 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="패턴 미감지 (HOLD)",
            invalidation="N/A",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="N/A",
        )
