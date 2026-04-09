"""
CandleScoreStrategy: 여러 캔들 패턴을 점수화하여 복합 신호 생성.

- 최근 봉 평가 (5개 항목):
  - 양봉 점수: +1 (close > open)
  - Upper shadow 없음 ((high-close)/(high-low) < 0.1): +1
  - Lower shadow 없음 ((close-low)/(high-low) > 0.9): +1
  - Volume 증가 (vol > vol.shift(1)): +1
  - Body 크기 (|close-open|/(high-low) > 0.6): +1
- bull_score = 해당 개수, bear_score = 반대 항목 개수
- BUY: bull_score >= 4, SELL: bear_score >= 4
- confidence: score == 5 → HIGH
- 최소 행: 15
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class CandleScoreStrategy(BaseStrategy):
    name = "candle_score"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 15:
            return self._hold(df, "데이터 부족")

        idx = len(df) - 2  # _last(df) = df.iloc[-2]
        row = df.iloc[idx]
        prev_row = df.iloc[idx - 1]

        o = float(row["open"])
        h = float(row["high"])
        lo = float(row["low"])
        c = float(row["close"])
        vol = float(row["volume"])
        prev_vol = float(prev_row["volume"])

        rng = h - lo
        if rng <= 0:
            return self._hold(df, "캔들 범위 0")

        bull_score = self._bull_score(o, h, lo, c, vol, prev_vol, rng)
        bear_score = self._bear_score(o, h, lo, c, vol, prev_vol, rng)

        entry = c

        if bull_score >= 4:
            conf = Confidence.HIGH if bull_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Bull score={bull_score}/5: 강한 양봉 패턴",
                invalidation=f"Close below open ({o:.2f})",
                bull_case=f"Bull score {bull_score}/5 달성, 강세 캔들",
                bear_case="Score 하락 시 신호 무효",
            )

        if bear_score >= 4:
            conf = Confidence.HIGH if bear_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Bear score={bear_score}/5: 강한 음봉 패턴",
                invalidation=f"Close above open ({o:.2f})",
                bull_case="Score 반전 시 신호 무효",
                bear_case=f"Bear score {bear_score}/5 달성, 약세 캔들",
            )

        return self._hold(df, f"Bull score={bull_score}, Bear score={bear_score}: 신호 없음")

    def _bull_score(
        self,
        o: float, h: float, lo: float, c: float,
        vol: float, prev_vol: float, rng: float,
    ) -> int:
        score = 0
        # 1. 양봉
        if c > o:
            score += 1
        # 2. upper shadow 없음 (close near high)
        if (h - c) / rng < 0.1:
            score += 1
        # 3. lower shadow 없음 (close near low → 아니라 open near low for bull)
        #    규칙: (close-low)/(high-low) > 0.9
        if (c - lo) / rng > 0.9:
            score += 1
        # 4. volume 증가
        if vol > prev_vol:
            score += 1
        # 5. body 크기
        if abs(c - o) / rng > 0.6:
            score += 1
        return score

    def _bear_score(
        self,
        o: float, h: float, lo: float, c: float,
        vol: float, prev_vol: float, rng: float,
    ) -> int:
        score = 0
        # 1. 음봉
        if c < o:
            score += 1
        # 2. lower shadow 없음 (close near low)
        if (c - lo) / rng < 0.1:
            score += 1
        # 3. upper shadow 없음 for bear → open near high
        #    반대 항목: (high-close)/(high-low) > 0.9
        if (h - c) / rng > 0.9:
            score += 1
        # 4. volume 증가
        if vol > prev_vol:
            score += 1
        # 5. body 크기
        if abs(c - o) / rng > 0.6:
            score += 1
        return score

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        entry = float(df["close"].iloc[-2]) if len(df) >= 2 else 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
