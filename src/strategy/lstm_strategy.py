"""
MLLSTMStrategy: LSTMSignalGenerator를 BaseStrategy 인터페이스로 래핑.

STRATEGY_REGISTRY에 "ml_lstm"으로 등록.
models/ 디렉토리에서 최신 LSTM 모델 자동 로드.
모델 없으면 HOLD, confidence=LOW 반환.
"""

import logging

import numpy as np
import pandas as pd

from src.ml.lstm_model import LSTMSignalGenerator
from src.ml.model import MLPrediction
from src.strategy.base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)


class MLLSTMStrategy(BaseStrategy):
    """
    LSTM ML 전략.

    startup: models/ 최신 pt/pkl 자동 로드.
    모델 없으면 fallback HOLD.
    """

    name = "ml_lstm"

    def __init__(self, symbol: str = "BTC/USDT"):
        self._generator = LSTMSignalGenerator(symbol=symbol)
        loaded = self._generator.load_latest()
        if not loaded:
            logger.info("MLLSTMStrategy: 모델 없음 — HOLD fallback 모드")

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = last["close"]

        # 모델 없을 때 heuristic fallback (return_5 + RSI 기반)
        if self._generator._model is None:
            pred = self._heuristic_predict(df, last)
        else:
            pred = self._generator.predict(df)

        action_map = {
            "BUY": Action.BUY,
            "SELL": Action.SELL,
            "HOLD": Action.HOLD,
        }
        action = action_map.get(pred.action, Action.HOLD)

        # confidence 매핑: 0.65+ → HIGH, 0.55+ → MEDIUM, else → LOW
        if pred.confidence >= 0.65:
            confidence = Confidence.HIGH
        elif pred.confidence >= 0.55:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        reasoning = (
            f"LSTM predict: {pred.action} (conf={pred.confidence:.3f}) "
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
            invalidation="LSTM 신호 반전 또는 confidence < 0.5",
            bull_case=f"p_buy={pred.proba_buy:.3f}",
            bear_case=f"p_sell={pred.proba_sell:.3f}",
        )

    def _heuristic_predict(self, df: pd.DataFrame, last: pd.Series) -> MLPrediction:
        """LSTM 모델 미학습 시 모멘텀 + RSI heuristic으로 신호 생성."""
        close = df["close"]
        rsi = float(last["rsi14"]) if "rsi14" in df.columns else 50.0

        # 단기 수익률 (5캔들)
        if len(close) >= 6:
            ret5 = float((close.iloc[-2] - close.iloc[-7]) / close.iloc[-7]) if close.iloc[-7] > 0 else 0.0
        else:
            ret5 = 0.0

        # 20캔들 변동성 대비 모멘텀
        if len(close) >= 21:
            vol20 = float(close.iloc[-21:-1].pct_change().std())
            threshold = vol20 * 0.5
        else:
            threshold = 0.002

        if ret5 > threshold and rsi < 70:
            return MLPrediction(
                action="BUY", confidence=0.60,
                proba_buy=0.60, proba_sell=0.20, proba_hold=0.20,
                model_name="heuristic_momentum_rsi",
                note="LSTM 모델 없음 — 단기 상승 모멘텀 + RSI 미과매수",
            )
        if ret5 < -threshold and rsi > 30:
            return MLPrediction(
                action="SELL", confidence=0.60,
                proba_buy=0.20, proba_sell=0.60, proba_hold=0.20,
                model_name="heuristic_momentum_rsi",
                note="LSTM 모델 없음 — 단기 하락 모멘텀 + RSI 미과매도",
            )
        return MLPrediction(
            action="HOLD", confidence=0.5,
            proba_buy=0.25, proba_sell=0.25, proba_hold=0.50,
            model_name="heuristic_momentum_rsi",
            note="LSTM 모델 없음 — 중립 구간",
        )
