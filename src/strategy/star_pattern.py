"""
Star Pattern 전략:
- Morning Star (BUY): 큰 음봉 → 작은 별봉(갭다운) → 큰 양봉(회복)
- Evening Star (SELL): 큰 양봉 → 작은 별봉(갭업) → 큰 음봉(회복)
- confidence: HIGH if 3봉 모두 완벽, MEDIUM if 부분 충족
- 최소 10행, idx = len(df) - 2
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 10


class StarPatternStrategy(BaseStrategy):
    name = "star_pattern"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        c1 = df.iloc[idx - 2]  # 첫째 봉 (큰 봉)
        c2 = df.iloc[idx - 1]  # 별봉
        c3 = df.iloc[idx]      # 세번째 봉 (확인 봉)
        atr = float(df["atr14"].iloc[idx])

        if atr <= 0:
            return self._hold(df, "ATR <= 0, cannot evaluate")

        # Morning Star 계산
        body1_bear = float(c1["open"]) - float(c1["close"])   # 양수 = 음봉
        body3_bull = float(c3["close"]) - float(c3["open"])   # 양수 = 양봉
        body2 = abs(float(c2["close"]) - float(c2["open"]))

        bearish1 = body1_bear > atr * 0.5    # 큰 음봉
        small2 = body2 < atr * 0.3           # 작은 별봉
        bullish3 = body3_bull > atr * 0.5    # 큰 양봉
        recovery = float(c3["close"]) > (float(c1["open"]) + float(c1["close"])) / 2

        # Evening Star 계산
        body1_bull = float(c1["close"]) - float(c1["open"])   # 양수 = 양봉
        body3_bear = float(c3["open"]) - float(c3["close"])   # 양수 = 음봉

        bullish1 = body1_bull > atr * 0.5    # 큰 양봉
        small2_eve = body2 < atr * 0.3       # 작은 별봉
        bearish3 = body3_bear > atr * 0.5    # 큰 음봉
        decline = float(c3["close"]) < (float(c1["open"]) + float(c1["close"])) / 2

        # Morning Star → BUY
        morning_conditions = [bearish1, small2, bullish3, recovery]
        morning_count = sum(morning_conditions)

        if morning_count >= 3:
            all_perfect = all(morning_conditions)
            confidence = Confidence.HIGH if all_perfect else Confidence.MEDIUM
            reason = (
                f"Morning Star: bearish1={bearish1}(body={body1_bear:.4f}>atr*0.5={atr*0.5:.4f}), "
                f"small2={small2}(body={body2:.4f}<atr*0.3={atr*0.3:.4f}), "
                f"bullish3={bullish3}(body={body3_bull:.4f}), recovery={recovery}"
            )
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c3["close"]),
                reasoning=reason,
                invalidation=f"Close below c2 low ({float(c2['low']):.2f})",
                bull_case="Morning Star reversal confirmed",
                bear_case="Pattern may fail if volume absent",
            )

        # Evening Star → SELL
        evening_conditions = [bullish1, small2_eve, bearish3, decline]
        evening_count = sum(evening_conditions)

        if evening_count >= 3:
            all_perfect = all(evening_conditions)
            confidence = Confidence.HIGH if all_perfect else Confidence.MEDIUM
            reason = (
                f"Evening Star: bullish1={bullish1}(body={body1_bull:.4f}>atr*0.5={atr*0.5:.4f}), "
                f"small2={small2_eve}(body={body2:.4f}<atr*0.3={atr*0.3:.4f}), "
                f"bearish3={bearish3}(body={body3_bear:.4f}), decline={decline}"
            )
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(c3["close"]),
                reasoning=reason,
                invalidation=f"Close above c2 high ({float(c2['high']):.2f})",
                bull_case="Pattern may fail if volume absent",
                bear_case="Evening Star reversal confirmed",
            )

        reason = (
            f"No star pattern: morning_score={morning_count}/4, evening_score={evening_count}/4, "
            f"atr={atr:.4f}"
        )
        return self._hold(df, reason)

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        price = float(df.iloc[-2]["close"]) if len(df) >= 2 else float(df.iloc[-1]["close"])
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
