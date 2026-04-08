"""
E2. Funding Rate Cash-and-Carry 전략.

원리: 시장중립 헷지
  - 스팟 매수 + 선물 숏 동시 진입 → 펀딩비만 수집
  - 펀딩비 양수(롱 지불) → 숏 포지션이 펀딩비 수신
  - 단일 심볼 백테스트: 신호만 생성 (헷지 실행은 라이브에서)

실증: Sharpe 1.66~3.5, Calmar 5~10 (ScienceDirect 2025)

df에 "funding_rate" 컬럼 있으면 사용, 없으면 RSI14 proxy 사용.
"""

import logging

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

# 연 환산 계수: 펀딩비는 8시간 단위, 연 3회/일 × 365일
ANNUALIZE = 3 * 365


class FundingCarryStrategy(BaseStrategy):
    """
    펀딩비 Cash-and-Carry 전략.

    entry_threshold 이상 펀딩비 → BUY (캐리 진입)
    exit_threshold 미만 펀딩비  → SELL (포지션 청산)
    """

    name = "funding_carry"

    def __init__(
        self,
        entry_threshold: float = 0.0003,   # +0.03%: 연 환산 ~32.85% 이상
        exit_threshold: float = 0.0001,    # +0.01%: 펀딩비 낮아지면 청산
        min_holding_candles: int = 8,      # 최소 8캔들 보유 (조기청산 방지)
    ):
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.min_holding_candles = min_holding_candles

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = last["close"]
        rsi = last.get("rsi14", 50.0)

        # funding_rate 컬럼 유무에 따라 분기
        if "funding_rate" in df.columns:
            fr = last["funding_rate"]
        else:
            fr = self._rsi_proxy(rsi)

        ann = fr * ANNUALIZE * 100  # 연 환산 %

        reasoning_base = f"funding_rate={fr:.4f}, 연환산={ann:.1f}%"

        if fr > self.entry_threshold:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Cash-and-carry 진입: {reasoning_base} > {self.entry_threshold:.4f}",
                invalidation=f"funding_rate < {self.exit_threshold:.4f} 또는 음수 전환",
                bull_case=f"펀딩비 {ann:.1f}% 수익 수집, 시장중립 헷지",
                bear_case="펀딩비 급락 시 조기청산 필요",
            )

        if fr < self.exit_threshold:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"캐리 청산: {reasoning_base} < {self.exit_threshold:.4f}",
                invalidation=f"funding_rate > {self.entry_threshold:.4f} 재진입",
                bull_case="",
                bear_case=f"펀딩비 수익 소멸, 헷지 포지션 청산",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"대기: {reasoning_base} (임계값 미달)",
            invalidation="",
            bull_case=f"entry_threshold={self.entry_threshold:.4f} 도달 시 진입",
            bear_case="",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _rsi_proxy(rsi: float) -> float:
        """funding_rate 컬럼 없을 때 RSI14로 대체."""
        if rsi > 70:
            return 0.0004   # 양수 펀딩비 proxy
        if rsi < 30:
            return -0.0002  # 음수 펀딩비 proxy
        return 0.0
