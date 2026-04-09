"""
MorningEveningStarStrategy: Morning Star (BUY) / Evening Star (SELL) 3봉 반전 패턴.
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class MorningEveningStarStrategy(BaseStrategy):
    name = "morning_evening_star"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 10:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 10행 필요)",
                invalidation="N/A",
            )

        idx = len(df) - 2   # 봉-1 (마지막 완성 캔들)
        idx2 = idx - 1      # 봉-2
        idx3 = idx - 2      # 봉-3

        o1 = float(df["open"].iloc[idx])
        c1 = float(df["close"].iloc[idx])
        o2 = float(df["open"].iloc[idx2])
        c2 = float(df["close"].iloc[idx2])
        o3 = float(df["open"].iloc[idx3])
        c3 = float(df["close"].iloc[idx3])

        body1 = abs(c1 - o1)
        body2 = abs(c2 - o2)
        body3 = abs(c3 - o3)

        atr = float(df["atr14"].iloc[idx]) if "atr14" in df.columns else 1.0
        if atr <= 0:
            atr = 1.0

        entry = float(df["close"].iloc[idx])

        # ── Morning Star (BUY) ────────────────────────────────────────────────
        # 봉-3: 강한 음봉 (body > ATR * 0.7)
        candle3_strong_bearish = (c3 < o3) and (body3 > atr * 0.7)
        # 봉-2: 작은 몸통 (body < ATR * 0.3)
        candle2_small = body2 < atr * 0.3
        # 봉-1: 강한 양봉이 봉-3 몸통의 50% 이상 회복
        # 봉-3 몸통: o3(top) ~ c3(bottom), recovery = c1 - c3 vs body3
        if candle3_strong_bearish and candle2_small and (c1 > o1):
            recovery = c1 - c3
            recovery_ratio = recovery / body3 if body3 > 0 else 0.0
            if recovery_ratio >= 0.5:
                confidence = Confidence.HIGH if recovery_ratio > 0.75 else Confidence.MEDIUM
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"Morning Star 패턴. "
                        f"봉-3 강한 음봉(body={body3:.4f}, ATR={atr:.4f}), "
                        f"봉-2 소형 몸통(body={body2:.4f}), "
                        f"봉-1 양봉 회복 {recovery_ratio*100:.1f}%."
                    ),
                    invalidation=f"봉-2 low {min(df['low'].iloc[idx2], df['low'].iloc[idx3]):.4f} 하회 시 무효",
                    bull_case="3봉 반전으로 하락 추세 종료 및 매수 전환",
                    bear_case="상위 저항 돌파 실패 시 재하락 가능",
                )

        # ── Evening Star (SELL) ───────────────────────────────────────────────
        # 봉-3: 강한 양봉 (body > ATR * 0.7)
        candle3_strong_bullish = (c3 > o3) and (body3 > atr * 0.7)
        # 봉-2: 작은 몸통
        # 봉-1: 강한 음봉이 봉-3 몸통의 50% 이상 침범
        # 침범 = o3+body3(top) - c1 vs body3
        if candle3_strong_bullish and candle2_small and (c1 < o1):
            penetration = c3 - c1  # 봉-3 close에서 봉-1 close까지 하락 거리
            penetration_ratio = penetration / body3 if body3 > 0 else 0.0
            if penetration_ratio >= 0.5:
                confidence = Confidence.HIGH if penetration_ratio > 0.75 else Confidence.MEDIUM
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"Evening Star 패턴. "
                        f"봉-3 강한 양봉(body={body3:.4f}, ATR={atr:.4f}), "
                        f"봉-2 소형 몸통(body={body2:.4f}), "
                        f"봉-1 음봉 침범 {penetration_ratio*100:.1f}%."
                    ),
                    invalidation=f"봉-2 high {max(df['high'].iloc[idx2], df['high'].iloc[idx3]):.4f} 상회 시 무효",
                    bull_case="하위 지지 존재 시 반등 가능",
                    bear_case="3봉 반전으로 상승 추세 종료 및 매도 전환",
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="Morning/Evening Star 패턴 미감지 (HOLD)",
            invalidation="N/A",
        )
