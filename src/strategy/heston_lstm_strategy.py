"""
F2. HestonLSTMStrategy: Heston 파라미터 + LSTM 예측 → 신호 생성.

기존 LSTMSignalGenerator를 활용:
- 기존 15 피처 + Heston 5 피처 = 20 피처로 확장
- 학습된 모델이 없을 경우 Heston v0 기반 규칙 fallback:
  - v0 < 0.0001 (저변동성) + theta < v0 (평균 회귀 예상) → BUY MEDIUM
  - v0 > 0.001 (고변동성) → HOLD
  - 기타 → HOLD
"""

import logging

import pandas as pd

from src.ml.heston_model import HestonVolatilityModel
from src.ml.lstm_model import LSTMSignalGenerator
from src.strategy.base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)


class HestonLSTMStrategy(BaseStrategy):
    """
    Heston 확률 변동성 파라미터 + LSTM 시계열 예측 하이브리드 전략.

    LSTM 모델 있으면: Heston 피처 포함 예측 사용.
    모델 없으면: Heston v0/theta 기반 규칙 fallback.
    """

    name = "heston_lstm"

    def __init__(self, symbol: str = "BTC/USDT"):
        self._heston = HestonVolatilityModel()
        self._lstm = LSTMSignalGenerator(symbol=symbol)
        self._model_loaded = self._lstm.load_latest()
        if not self._model_loaded:
            logger.info("HestonLSTMStrategy: LSTM 모델 없음 — Heston 규칙 기반 fallback")

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = float(last["close"])

        # Heston 파라미터 추정
        params = self._heston.estimate(df)
        v0 = params["v0"]
        theta = params["theta"]

        if self._model_loaded:
            return self._generate_lstm(df, params, entry)
        else:
            return self._generate_fallback(params, entry)

    def _generate_lstm(self, df: pd.DataFrame, params: dict, entry: float) -> Signal:
        """LSTM 예측 + Heston 파라미터 메타 정보 추가."""
        pred = self._lstm.predict(df)

        action_map = {"BUY": Action.BUY, "SELL": Action.SELL, "HOLD": Action.HOLD}
        action = action_map.get(pred.action, Action.HOLD)

        if pred.confidence >= 0.65:
            confidence = Confidence.HIGH
        elif pred.confidence >= 0.55:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        v0 = params["v0"]
        reasoning = (
            f"Heston+LSTM: {pred.action} conf={pred.confidence:.3f} "
            f"v0={v0:.6f} kappa={params['kappa']:.3f} theta={params['theta']:.6f} "
            f"model={pred.model_name}"
        )

        return Signal(
            action=action,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry,
            reasoning=reasoning,
            invalidation="LSTM 신호 반전 또는 Heston v0 > 0.001 (고변동성)",
            bull_case=f"p_buy={pred.proba_buy:.3f} v0={v0:.6f}(저변동)",
            bear_case=f"p_sell={pred.proba_sell:.3f} v0={v0:.6f}(고변동)",
        )

    def _generate_fallback(self, params: dict, entry: float) -> Signal:
        """LSTM 모델 없을 때 Heston 규칙 기반 신호."""
        v0 = params["v0"]
        theta = params["theta"]

        # 저변동성 + 평균 회귀 예상 → BUY MEDIUM
        if v0 < 0.0001 and theta < v0:
            action = Action.BUY
            confidence = Confidence.MEDIUM
            reasoning = (
                f"Heston fallback: 저변동성(v0={v0:.6f}) + 평균회귀 예상(theta={theta:.6f} < v0)"
            )
            bull_case = f"v0={v0:.6f} 저변동, 상승 여지"
            bear_case = "변동성 급등 시 무효"
        # 고변동성 → HOLD
        elif v0 > 0.001:
            action = Action.HOLD
            confidence = Confidence.LOW
            reasoning = f"Heston fallback: 고변동성 리스크 회피(v0={v0:.6f})"
            bull_case = ""
            bear_case = f"v0={v0:.6f} 고변동성"
        # 기타 → HOLD
        else:
            action = Action.HOLD
            confidence = Confidence.LOW
            reasoning = f"Heston fallback: 중립(v0={v0:.6f} theta={theta:.6f})"
            bull_case = ""
            bear_case = ""

        return Signal(
            action=action,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry,
            reasoning=reasoning,
            invalidation="Heston v0 변화 또는 LSTM 모델 학습 후 재평가",
            bull_case=bull_case,
            bear_case=bear_case,
        )
