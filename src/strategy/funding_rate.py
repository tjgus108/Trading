"""
A1. Funding Rate 역추세 전략.

원리: 펀딩비 과열(롱 과밀/숏 과밀) 시 반대 방향 진입.
  - 펀딩비 > +0.03% → 롱 과밀 → SELL (숏)
  - 펀딩비 < -0.01% → 숏 과밀 → BUY (롱)

실증: Sharpe 1.66~3.5, Calmar 5~10 (ScienceDirect 2025)
데이터: Binance 선물 API, 8시간 갱신

외부에서 update_funding_rate(rate)를 호출해 주입.
데이터 없을 때 price-action 기반 proxy(RSI 과매수/과매도) 대체.
"""

import logging
from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

# 펀딩비 임계값 (Binance 기본: 0.01%, 과열 기준 3배)
LONG_EXTREME = 0.0003   # +0.03%: 롱 과밀 → 숏
SHORT_EXTREME = -0.0001  # -0.01%: 숏 과밀 → 롱
VERY_EXTREME = 0.0005    # +0.05%: 매우 강한 롱 과밀


class FundingRateStrategy(BaseStrategy):
    """
    펀딩비 역추세 전략.

    orchestrator에서 주기적으로 update_funding_rate()를 호출해야 함.
    펀딩비 없으면 RSI 기반 proxy로 자동 대체.
    """

    name = "funding_rate"

    def __init__(
        self,
        long_threshold: float = LONG_EXTREME,
        short_threshold: float = SHORT_EXTREME,
        rsi_confirm: bool = True,
    ):
        self.long_threshold = long_threshold    # 이 이상이면 SELL
        self.short_threshold = short_threshold  # 이 이하면 BUY
        self.rsi_confirm = rsi_confirm          # RSI로 진입 확인 여부
        self._funding_rate: Optional[float] = None
        self._funding_rate_history: list[float] = []

    def update_funding_rate(self, rate: float) -> None:
        """외부(orchestrator/data-agent)에서 최신 펀딩비 주입."""
        self._funding_rate = rate
        self._funding_rate_history.append(rate)
        # 최근 20개만 유지 (약 6일치 8h 주기)
        if len(self._funding_rate_history) > 20:
            self._funding_rate_history = self._funding_rate_history[-20:]
        logger.debug("Funding rate updated: %.4f%%", rate * 100)

    def get_funding_rate(self) -> Optional[float]:
        return self._funding_rate

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = last["close"]
        rsi = last["rsi14"]
        atr = last["atr14"]

        fr = self._funding_rate

        if fr is not None:
            return self._signal_from_funding_rate(fr, entry, rsi, atr)
        else:
            # fallback: RSI 극단 = 펀딩비 대리 신호
            return self._proxy_signal(entry, rsi, atr)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _signal_from_funding_rate(
        self, fr: float, entry: float, rsi: float, atr: float
    ) -> Signal:
        bull_case = f"FR={fr*100:.4f}% 숏 과밀 → 롱 반등 기대, RSI={rsi:.1f}"
        bear_case = f"FR={fr*100:.4f}% 롱 과밀 → 숏 역추세, RSI={rsi:.1f}"

        # 롱 과밀: 숏 진입
        if fr >= self.long_threshold:
            # RSI 추가 확인 (선택): 과매수권이면 신호 강화
            if self.rsi_confirm and rsi < 45:
                # 펀딩비는 과열이지만 RSI가 아직 안 떨어졌으면 MEDIUM
                confidence = Confidence.MEDIUM
            else:
                confidence = Confidence.HIGH if fr >= VERY_EXTREME else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Funding rate {fr*100:.4f}% ≥ {self.long_threshold*100:.4f}%: 롱 과밀 역추세",
                invalidation=f"FR 정상화 ({self.long_threshold*100:.4f}% 미만) 또는 RSI > 70",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 숏 과밀: 롱 진입
        if fr <= self.short_threshold:
            if self.rsi_confirm and rsi > 55:
                confidence = Confidence.MEDIUM
            else:
                confidence = Confidence.HIGH
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Funding rate {fr*100:.4f}% ≤ {self.short_threshold*100:.4f}%: 숏 과밀 역추세",
                invalidation=f"FR 정상화 ({self.short_threshold*100:.4f}% 초과) 또는 RSI < 30",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"Funding rate {fr*100:.4f}%: 정상 범위 ({self.short_threshold*100:.4f}%~{self.long_threshold*100:.4f}%)",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )

    def _proxy_signal(self, entry: float, rsi: float, atr: float) -> Signal:
        """펀딩비 없을 때 RSI 극단값으로 대체 (보수적)."""
        note = "funding_rate=None, RSI proxy 사용"

        if rsi >= 80:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"RSI proxy: {rsi:.1f} ≥ 80 (펀딩비 없음)",
                invalidation="RSI < 70",
                bull_case="",
                bear_case=note,
            )
        if rsi <= 20:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"RSI proxy: {rsi:.1f} ≤ 20 (펀딩비 없음)",
                invalidation="RSI > 30",
                bull_case=note,
                bear_case="",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning="펀딩비 미제공, RSI 중립 → HOLD",
            invalidation="",
            bull_case=note,
            bear_case=note,
        )
