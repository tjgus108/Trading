"""
LiquidationCascadeStrategy: 연쇄 청산 예측 기반 역추세 전략.

로직:
  1. LiquidationFetcher로 청산 압력 계산
  2. cascade_risk=True (청산 급증): 방어적 HOLD
  3. liq_ratio > 0.75 (롱 청산 우세): 반등 매수 (BUY) — 과청산 후 반전
  4. liq_ratio < 0.25 (숏 청산 우세): 반락 매도 (SELL)
  5. 기타: HOLD

추가 필터:
  - RSI < 35 AND liq_ratio > 0.75 → HIGH confidence BUY
  - RSI > 65 AND liq_ratio < 0.25 → HIGH confidence SELL
  - 조건 하나만 충족 → MEDIUM confidence
"""

import pandas as pd

from src.data.liquidation_feed import LiquidationFetcher
from .base import Action, BaseStrategy, Confidence, Signal


class LiquidationCascadeStrategy(BaseStrategy):
    name = "liquidation_cascade"

    def __init__(self) -> None:
        self._fetcher = LiquidationFetcher()

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])
        rsi = float(last.get("rsi14", 50))

        pressure = self._fetcher.compute_pressure()

        long_k = pressure.long_liq_usd / 1000
        short_k = pressure.short_liq_usd / 1000
        ratio = pressure.liq_ratio

        liq_info = (
            f"long_liq=${long_k:.0f}K short_liq=${short_k:.0f}K ratio={ratio:.2f}"
        )

        # cascade_risk → 방어적 HOLD
        if pressure.cascade_risk:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Cascade risk detected — defensive HOLD. {liq_info}",
                invalidation="Cascade risk subsides",
            )

        # 롱 청산 우세 → 반등 BUY
        if ratio > 0.75:
            rsi_filter = rsi < 35
            confidence = Confidence.HIGH if rsi_filter else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Long liquidation cascade — contrarian BUY. "
                    f"RSI={rsi:.1f}. {liq_info}"
                ),
                invalidation="liq_ratio drops below 0.75 or cascade_risk=True",
                bull_case=f"Over-liquidation reversal. {liq_info}",
                bear_case="Cascade continues, further downside.",
            )

        # 숏 청산 우세 → 반락 SELL
        if ratio < 0.25:
            rsi_filter = rsi > 65
            confidence = Confidence.HIGH if rsi_filter else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Short liquidation cascade — contrarian SELL. "
                    f"RSI={rsi:.1f}. {liq_info}"
                ),
                invalidation="liq_ratio rises above 0.25 or cascade_risk=True",
                bull_case="Short squeeze may continue.",
                bear_case=f"Over-liquidation reversal downward. {liq_info}",
            )

        # 중립 → HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Neutral liquidation pressure — HOLD. {liq_info}",
            invalidation="liq_ratio exceeds thresholds",
        )
