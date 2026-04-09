"""
ThreeSoldiersAndCrowsStrategy: Three White Soldiers (BUY) / Three Black Crows (SELL).
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class ThreeSoldiersAndCrowsStrategy(BaseStrategy):
    name = "three_soldiers_crows"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 8:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 8행 필요)",
                invalidation="N/A",
            )

        idx = len(df) - 2   # 봉-1 (마지막 완성)
        idx2 = idx - 1      # 봉-2
        idx3 = idx - 2      # 봉-3

        o1 = float(df["open"].iloc[idx])
        c1 = float(df["close"].iloc[idx])
        h1 = float(df["high"].iloc[idx])
        l1 = float(df["low"].iloc[idx])

        o2 = float(df["open"].iloc[idx2])
        c2 = float(df["close"].iloc[idx2])
        h2 = float(df["high"].iloc[idx2])
        l2 = float(df["low"].iloc[idx2])

        o3 = float(df["open"].iloc[idx3])
        c3 = float(df["close"].iloc[idx3])
        h3 = float(df["high"].iloc[idx3])
        l3 = float(df["low"].iloc[idx3])

        body1 = abs(c1 - o1)
        body2 = abs(c2 - o2)
        body3 = abs(c3 - o3)

        range1 = h1 - l1 if (h1 - l1) > 0 else 1e-9
        range2 = h2 - l2 if (h2 - l2) > 0 else 1e-9
        range3 = h3 - l3 if (h3 - l3) > 0 else 1e-9

        atr = float(df["atr14"].iloc[idx]) if "atr14" in df.columns else 1.0
        if atr <= 0:
            atr = 1.0

        entry = float(df["close"].iloc[idx])
        avg_body = (body1 + body2 + body3) / 3.0

        # ── Three White Soldiers (BUY) ────────────────────────────────────────
        all_bullish = (c1 > o1) and (c2 > o2) and (c3 > o3)
        ascending_close = (c1 > c2) and (c2 > c3)
        strong_bodies = (
            body1 > range1 * 0.6
            and body2 > range2 * 0.6
            and body3 > range3 * 0.6
        )

        if all_bullish and ascending_close and strong_bodies:
            confidence = Confidence.HIGH if avg_body > atr * 0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Three White Soldiers 패턴. "
                    f"3봉 연속 양봉, 상승 close, "
                    f"평균 body={avg_body:.4f} (ATR={atr:.4f})."
                ),
                invalidation=f"봉-3 open {o3:.4f} 하회 시 무효",
                bull_case="강한 매수세로 연속 상승 확인, 추세 전환 신호",
                bear_case="과매수 구간 진입 시 단기 조정 가능",
            )

        # ── Three Black Crows (SELL) ───────────────────────────────────────────
        all_bearish = (c1 < o1) and (c2 < o2) and (c3 < o3)
        descending_close = (c1 < c2) and (c2 < c3)
        strong_bodies_bear = (
            body1 > range1 * 0.6
            and body2 > range2 * 0.6
            and body3 > range3 * 0.6
        )

        if all_bearish and descending_close and strong_bodies_bear:
            confidence = Confidence.HIGH if avg_body > atr * 0.8 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Three Black Crows 패턴. "
                    f"3봉 연속 음봉, 하락 close, "
                    f"평균 body={avg_body:.4f} (ATR={atr:.4f})."
                ),
                invalidation=f"봉-3 open {o3:.4f} 상회 시 무효",
                bull_case="하위 지지 존재 시 반등 가능",
                bear_case="강한 매도세로 연속 하락 확인, 추세 전환 신호",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="Three Soldiers/Crows 패턴 미감지 (HOLD)",
            invalidation="N/A",
        )
