"""
C1. MLStrategy: MLSignalGenerator를 BaseStrategy 인터페이스로 래핑.

STRATEGY_REGISTRY에 "ml_rf"로 등록.
models/ 디렉토리에서 최신 모델 자동 로드.
모델 없으면 HOLD, confidence=LOW 반환.

tournament 참여 가능: backtest 시 ML 모델로 신호 생성.
"""

import logging

import numpy as np
import pandas as pd

from src.ml.model import MLPrediction, MLSignalGenerator
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
        last = self._last(df)
        entry = last["close"]

        # 모델 없을 때 heuristic fallback (EMA + RSI 기반)
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

    def _heuristic_predict(self, df: pd.DataFrame, last: pd.Series) -> MLPrediction:
        """모델 미학습 시 EMA + RSI heuristic으로 신호 생성."""
        # EMA 크로스오버
        ema20 = float(last["ema20"]) if "ema20" in df.columns else 0.0
        ema50 = float(last["ema50"]) if "ema50" in df.columns else 0.0
        rsi = float(last["rsi14"]) if "rsi14" in df.columns else 50.0
        close = float(last["close"])

        # 이전 캔들 (idx = len(df) - 2 이므로 -3번째가 그 이전)
        if len(df) >= 3 and "ema20" in df.columns and "ema50" in df.columns:
            prev = df.iloc[-3]
            prev_ema20 = float(prev["ema20"])
            prev_ema50 = float(prev["ema50"])
            golden_cross = (prev_ema20 <= prev_ema50) and (ema20 > ema50)
            death_cross = (prev_ema20 >= prev_ema50) and (ema20 < ema50)
        else:
            golden_cross = ema20 > ema50 and rsi < 45
            death_cross = ema20 < ema50 and rsi > 55

        if golden_cross and rsi < 70:
            return MLPrediction(
                action="BUY", confidence=0.62,
                proba_buy=0.62, proba_sell=0.18, proba_hold=0.20,
                model_name="heuristic_ema_rsi",
                note="모델 없음 — EMA 골든크로스 + RSI 과매도 아님",
            )
        if death_cross and rsi > 30:
            return MLPrediction(
                action="SELL", confidence=0.62,
                proba_buy=0.18, proba_sell=0.62, proba_hold=0.20,
                model_name="heuristic_ema_rsi",
                note="모델 없음 — EMA 데드크로스 + RSI 과매수 아님",
            )
        # 추세 추종 (강한 추세)
        if ema20 > ema50 and rsi > 55 and rsi < 70:
            return MLPrediction(
                action="BUY", confidence=0.58,
                proba_buy=0.58, proba_sell=0.22, proba_hold=0.20,
                model_name="heuristic_ema_rsi",
                note="모델 없음 — EMA 상승 추세 + RSI 모멘텀",
            )
        if ema20 < ema50 and rsi < 45 and rsi > 30:
            return MLPrediction(
                action="SELL", confidence=0.58,
                proba_buy=0.22, proba_sell=0.58, proba_hold=0.20,
                model_name="heuristic_ema_rsi",
                note="모델 없음 — EMA 하락 추세 + RSI 약세",
            )
        return MLPrediction(
            action="HOLD", confidence=0.5,
            proba_buy=0.25, proba_sell=0.25, proba_hold=0.50,
            model_name="heuristic_ema_rsi",
            note="모델 없음 — 중립 구간",
        )
