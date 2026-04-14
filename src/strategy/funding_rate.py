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
from typing import Optional, List

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

# 펀딩비 임계값 (Binance 기본: 0.01%, 완화된 기준으로 신호 빈도 향상)
LONG_EXTREME = 0.00015  # +0.015%: 롱 과밀 → 숏 (기존 0.03% → 완화)
SHORT_EXTREME = -0.00005  # -0.005%: 숏 과밀 → 롱 (기존 -0.01% → 완화)
VERY_EXTREME = 0.0003    # +0.03%: 매우 강한 롱 과밀 (기존 0.05% → 완화)

# 약세 필터: 평균 펀딩비가 이 값 미만이면 BUY 억제 (지속적 숏 bias 시장)
BEARISH_MEAN_THRESHOLD = -0.00003  # -0.003%
# 급변 서킷: Z-score 절대값이 이 이상이면 HOLD (노이즈 방지)
SPIKE_ZSCORE_THRESHOLD = 3.0


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
        bearish_mean_threshold: float = BEARISH_MEAN_THRESHOLD,
        spike_zscore_threshold: float = SPIKE_ZSCORE_THRESHOLD,
    ):
        self.long_threshold = long_threshold    # 이 이상이면 SELL
        self.short_threshold = short_threshold  # 이 이하면 BUY
        self.rsi_confirm = rsi_confirm          # RSI로 진입 확인 여부
        self.bearish_mean_threshold = bearish_mean_threshold  # BUY 억제 평균 임계값
        self.spike_zscore_threshold = spike_zscore_threshold  # 급변 서킷 Z-score 임계값
        self._funding_rate: Optional[float] = None
        self._funding_rate_history: List[float] = []

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

    def _mean_funding_rate(self) -> Optional[float]:
        """히스토리 평균 펀딩비. 데이터 3개 미만이면 None."""
        if len(self._funding_rate_history) < 3:
            return None
        return float(np.mean(self._funding_rate_history))

    def _funding_rate_zscore(self, fr: float) -> Optional[float]:
        """현재 펀딩비의 Z-score. 데이터 3개 미만이면 None."""
        if len(self._funding_rate_history) < 3:
            return None
        arr = np.array(self._funding_rate_history)
        std = float(np.std(arr))
        if std == 0:
            return 0.0
        mean = float(np.mean(arr))
        return (fr - mean) / std

    def _is_spike(self, fr: float) -> bool:
        """현재 펀딩비가 급변(Z-score 초과) 여부."""
        z = self._funding_rate_zscore(fr)
        if z is None:
            return False
        return abs(z) >= self.spike_zscore_threshold

    def _is_bearish_market(self) -> bool:
        """평균 펀딩비가 bearish_mean_threshold 미만 → 약세 시장."""
        mean = self._mean_funding_rate()
        if mean is None:
            return False
        return mean < self.bearish_mean_threshold

    def _signal_from_funding_rate(
        self, fr: float, entry: float, rsi: float, atr: float
    ) -> Signal:
        bull_case = f"FR={fr*100:.4f}% 숏 과밀 → 롱 반등 기대, RSI={rsi:.1f}"
        bear_case = f"FR={fr*100:.4f}% 롱 과밀 → 숏 역추세, RSI={rsi:.1f}"

        # 급변 서킷: Z-score 임계 초과 시 HOLD
        if self._is_spike(fr):
            z = self._funding_rate_zscore(fr)
            logger.warning("Funding rate spike detected: z=%.2f, fr=%.4f%%. HOLD.", z, fr * 100)
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"FR spike Z={z:.2f} ≥ {self.spike_zscore_threshold} → 서킷 HOLD",
                invalidation="Z-score 정상화",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 롱 과밀: 숏 진입
        if fr >= self.long_threshold:
            # RSI 추가 확인 (선택): 과매수권이면 신호 강화 (임계값 완화: 45→55)
            if self.rsi_confirm and rsi < 55:
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
            # 약세장 필터: 평균 펀딩비가 임계치 미만이면 BUY 억제 → HOLD
            if self._is_bearish_market():
                mean = self._mean_funding_rate()
                logger.info(
                    "Bearish market filter: mean FR=%.4f%% < threshold=%.4f%%. BUY suppressed.",
                    mean * 100, self.bearish_mean_threshold * 100,
                )
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"FR={fr*100:.4f}% 숏 과밀이나 평균FR={mean*100:.4f}% < "
                        f"{self.bearish_mean_threshold*100:.4f}% → 약세 필터 BUY 억제"
                    ),
                    invalidation=f"평균FR {self.bearish_mean_threshold*100:.4f}% 이상 회복",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

            if self.rsi_confirm and rsi > 45:  # 임계값 완화: 55→45
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
