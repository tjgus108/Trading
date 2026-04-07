"""
C1. MLStrategy: MLSignalGenerator를 BaseStrategy 인터페이스로 래핑.

STRATEGY_REGISTRY에 "ml_rf"로 등록.
models/ 디렉토리에서 최신 모델 자동 로드.
모델 없으면 HOLD, confidence=LOW 반환.

tournament 참여 가능: backtest 시 ML 모델로 신호 생성.
"""

import logging

import pandas as pd

from src.ml.model import MLSignalGenerator
from src.strategy.base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)


class MLRFStrategy(BaseStrategy):
    """
    RandomForest ML 전략.

    startup: models/ 최신 pkl 자동 로드.
    모델 없으면 fallback HOLD.
    """

    name = "ml_rf"

    def __init__(self, symbol: str = "BTC/USDT"):
        self._generator = MLSignalGenerator(symbol=symbol)
        # 자동 로드 시도 (실패해도 계속)
        loaded = self._generator.load_latest()
        if not loaded:
            logger.info("MLRFStrategy: 모델 없음 — HOLD fallback 모드")

    def generate(self, df: pd.DataFrame) -> Signal:
        pred = self._generator.predict(df)
        last = self._last(df)
        entry = last["close"]

        action_map = {
            "BUY": Action.BUY,
            "SELL": Action.SELL,
            "HOLD": Action.HOLD,
        }
        action = action_map.get(pred.action, Action.HOLD)

        # confidence 매핑: 확률 0.6+ → HIGH, 0.5+ → MEDIUM, else → LOW
        if pred.confidence >= 0.65:
            confidence = Confidence.HIGH
        elif pred.confidence >= 0.55:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        reasoning = (
            f"RF predict: {pred.action} (conf={pred.confidence:.3f}) "
            f"p_buy={pred.proba_buy:.3f} p_sell={pred.proba_sell:.3f} "
            f"model={pred.model_name}"
        )
        note = pred.note if pred.note else ""

        return Signal(
            action=action,
            confidence=confidence,
            strategy=self.name,
            entry_price=entry,
            reasoning=reasoning + (f" [{note}]" if note else ""),
            invalidation="ML 신호 반전 또는 confidence < 0.5",
            bull_case=f"p_buy={pred.proba_buy:.3f}",
            bear_case=f"p_sell={pred.proba_sell:.3f}",
        )
