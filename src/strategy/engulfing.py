"""
EngulfingStrategy: Bullish/Bearish Engulfing 패턴 전략.
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class EngulfingStrategy(BaseStrategy):
    name = "engulfing"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        if len(df) < 5:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (최소 5행 필요)",
                invalidation="N/A",
            )

        idx = len(df) - 2  # 마지막 완성 캔들 (현재봉)
        prev_idx = idx - 1  # 이전봉

        open_curr = float(df["open"].iloc[idx])
        close_curr = float(df["close"].iloc[idx])
        open_prev = float(df["open"].iloc[prev_idx])
        close_prev = float(df["close"].iloc[prev_idx])

        body_curr = abs(close_curr - open_curr)
        body_prev = abs(close_prev - open_prev)

        # ── Bullish Engulfing ─────────────────────────────────────────────
        # 이전봉 음봉 AND 현재봉이 이전봉을 완전히 감쌈
        is_bullish_engulfing = (
            close_prev < open_prev              # 이전봉 음봉
            and open_curr <= close_prev         # 현재봉 open이 이전봉 close 이하
            and close_curr >= open_prev         # 현재봉 close가 이전봉 open 이상
        )

        # ── Bearish Engulfing ─────────────────────────────────────────────
        # 이전봉 양봉 AND 현재봉이 이전봉을 완전히 감쌈
        is_bearish_engulfing = (
            close_prev > open_prev              # 이전봉 양봉
            and open_curr >= close_prev         # 현재봉 open이 이전봉 close 이상
            and close_curr <= open_prev         # 현재봉 close가 이전봉 open 이하
        )

        # confidence: 현재봉 body > 이전봉 body * 1.5 이면 HIGH
        strong = body_prev > 0 and body_curr > body_prev * 1.5
        confidence = Confidence.HIGH if strong else Confidence.MEDIUM

        if is_bullish_engulfing:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bullish Engulfing 패턴. "
                    f"이전봉(O={open_prev:.4f}, C={close_prev:.4f}) 음봉을 "
                    f"현재봉(O={open_curr:.4f}, C={close_curr:.4f})이 감쌈."
                ),
                invalidation=f"현재봉 close {close_curr:.4f} 하회 시 무효",
                bull_case="강한 매수세로 이전 음봉을 완전히 상쇄",
                bear_case="상위 저항선 존재 시 추가 상승 제한 가능",
            )

        if is_bearish_engulfing:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Bearish Engulfing 패턴. "
                    f"이전봉(O={open_prev:.4f}, C={close_prev:.4f}) 양봉을 "
                    f"현재봉(O={open_curr:.4f}, C={close_curr:.4f})이 감쌈."
                ),
                invalidation=f"현재봉 close {close_curr:.4f} 상회 시 무효",
                bull_case="하위 지지선 존재 시 반등 가능",
                bear_case="강한 매도세로 이전 양봉을 완전히 상쇄",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning="Engulfing 패턴 미감지 (HOLD)",
            invalidation="N/A",
        )
