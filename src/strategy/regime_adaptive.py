"""
E1. RegimeAdaptiveStrategy: HMM 레짐 탐지 기반 적응형 전략.

bull 레짐 → MLRFStrategy (공격적)
bear 레짐 → ResidualMeanReversionStrategy (보수적)
레짐 전환 시 → LOW confidence
모델/데이터 부족 → HOLD fallback
"""

import logging

import pandas as pd

from src.ml.hmm_model import HMMRegimeDetector
from src.strategy.base import Action, BaseStrategy, Confidence, Signal
from src.strategy.ml_strategy import MLRFStrategy
from src.strategy.residual_mean_reversion import ResidualMeanReversionStrategy

logger = logging.getLogger(__name__)

MIN_ROWS = 30  # 레짐 탐지 최소 행 수


class RegimeAdaptiveStrategy(BaseStrategy):
    """
    HMM 레짐 적응형 전략.

    bull → MLRFStrategy, bear → ResidualMeanReversionStrategy
    레짐 전환 시 confidence=LOW.
    """

    name = "regime_adaptive"

    def __init__(self):
        self._hmm = HMMRegimeDetector()
        self._bull_strategy = MLRFStrategy()
        self._bear_strategy = ResidualMeanReversionStrategy()
        self._prev_regime: int | None = None

    def generate(self, df: pd.DataFrame) -> Signal:
        # 데이터 부족 → HOLD
        if df is None or len(df) < MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        last = self._last(df)
        entry = float(last["close"])

        # 레짐 탐지
        try:
            seq = self._hmm.predict_sequence(df)
            if seq is None or len(seq) < 2:
                return self._hold_signal(entry, "레짐 시퀀스 계산 실패")

            current_regime = int(seq.iloc[-2])  # _last(df) 기준 (-2)
        except Exception as e:
            logger.warning("HMM predict 실패: %s", e)
            return self._hold_signal(entry, f"HMM 오류: {e}")

        # 레짐 전환 여부 확인
        regime_switched = (
            self._prev_regime is not None and self._prev_regime != current_regime
        )
        self._prev_regime = current_regime

        # 레짐별 전략 신호 생성
        try:
            if current_regime == 1:  # bull
                sub_signal = self._bull_strategy.generate(df)
                regime_label = "bull"
            else:  # bear
                sub_signal = self._bear_strategy.generate(df)
                regime_label = "bear"
        except Exception as e:
            logger.warning("서브 전략 신호 생성 실패: %s", e)
            return self._hold_signal(entry, f"서브 전략 오류: {e}")

        # 레짐 전환 시 confidence 강제 LOW
        confidence = Confidence.LOW if regime_switched else sub_signal.confidence

        reasoning = (
            f"[{regime_label.upper()} regime] {sub_signal.reasoning}"
            + (" [레짐 전환 — 불확실성↑]" if regime_switched else "")
        )

        return Signal(
            action=sub_signal.action,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry,
            reasoning=reasoning,
            invalidation=sub_signal.invalidation,
            bull_case=sub_signal.bull_case,
            bear_case=sub_signal.bear_case,
        )

    def _hold_signal(self, entry: float, reason: str) -> Signal:
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
