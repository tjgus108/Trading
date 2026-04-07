"""
C1. MLSignalGenerator: RandomForest 기반 신호 생성기.

alpha-agent와 호환 인터페이스:
  predict(df) → {"action": "BUY"|"SELL"|"HOLD", "confidence": 0~1, "proba": {...}}

설계:
  - 모델 없으면 HOLD, confidence=0 반환
  - sklearn RandomForest (초기) — 추후 LSTM으로 고도화
  - 모델 파일: models/<strategy>_<date>.pkl
  - 최소 성과 기준: test accuracy > 55%
  - 미래 데이터 누출 방지: WalkForwardTrainer가 담당
"""

import logging
import os
import pickle
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.ml.features import FeatureBuilder

logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MIN_ACCURACY = 0.55  # 최소 정확도 기준


@dataclass
class MLPrediction:
    action: str             # "BUY" | "SELL" | "HOLD"
    confidence: float       # 0.0~1.0
    proba_buy: float
    proba_sell: float
    proba_hold: float
    model_name: str
    note: str = ""

    def summary(self) -> str:
        return (
            f"ML_SIGNAL:\n"
            f"  action: {self.action}\n"
            f"  confidence: {self.confidence:.3f}\n"
            f"  proba_buy: {self.proba_buy:.3f}\n"
            f"  proba_sell: {self.proba_sell:.3f}\n"
            f"  model: {self.model_name}\n"
            f"  note: {self.note}"
        )


class MLSignalGenerator:
    """
    RandomForest 기반 ML 신호 생성기.

    사용법:
        gen = MLSignalGenerator()
        gen.load("models/rf_btc_2024-01-01.pkl")  # 또는 자동 로드
        pred = gen.predict(df)
    """

    def __init__(
        self,
        symbol: str = "BTC/USDT",
        forward_n: int = 5,
        threshold: float = 0.003,
    ):
        self.symbol = symbol
        self.feature_builder = FeatureBuilder(forward_n=forward_n, threshold=threshold)
        self._model = None
        self._model_name: str = "no model"
        self._label_map: dict[int, str] = {1: "BUY", -1: "SELL", 0: "HOLD"}
        self._class_order: Optional[list[int]] = None  # 모델의 class 순서

    def load(self, path: str) -> bool:
        """모델 파일 로드. 실패 시 False 반환."""
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            self._model = data["model"]
            self._model_name = data.get("name", Path(path).stem)
            self._class_order = data.get("class_order", [-1, 0, 1])
            logger.info("ML model loaded: %s", self._model_name)
            return True
        except Exception as e:
            logger.warning("ML model load failed (%s): %s", path, e)
            return False

    def load_latest(self) -> bool:
        """models/ 디렉토리에서 최신 모델 자동 로드."""
        MODELS_DIR.mkdir(exist_ok=True)
        pkls = sorted(MODELS_DIR.glob("*.pkl"), reverse=True)
        if not pkls:
            logger.info("No ML model found in %s", MODELS_DIR)
            return False
        return self.load(str(pkls[0]))

    def predict(self, df: pd.DataFrame) -> MLPrediction:
        """
        마지막 완성 캔들 기준 신호 예측.
        모델 없으면 HOLD, confidence=0 반환.
        """
        if self._model is None:
            return MLPrediction(
                action="HOLD", confidence=0.0,
                proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
                model_name="no model trained",
                note="모델 없음 — WalkForwardTrainer로 학습 필요",
            )

        try:
            feat_df = self.feature_builder.build_features_only(df)
            if feat_df.empty:
                return self._hold("피처 계산 실패")

            # 마지막 완성 캔들 (-2번째)
            if len(feat_df) < 2:
                return self._hold("피처 데이터 부족")

            X = feat_df.iloc[[-2]]  # shape (1, n_features)
            proba = self._model.predict_proba(X)[0]
            classes = self._class_order or list(self._model.classes_)

            # class → proba 매핑
            proba_map = dict(zip(classes, proba))
            p_buy = proba_map.get(1, 0.0)
            p_sell = proba_map.get(-1, 0.0)
            p_hold = proba_map.get(0, 0.0)

            # 가장 높은 확률의 클래스 선택
            pred_class = max(proba_map, key=proba_map.get)
            action = self._label_map.get(pred_class, "HOLD")
            confidence = float(proba_map[pred_class])

            return MLPrediction(
                action=action,
                confidence=confidence,
                proba_buy=float(p_buy),
                proba_sell=float(p_sell),
                proba_hold=float(p_hold),
                model_name=self._model_name,
            )

        except Exception as e:
            logger.error("ML predict error: %s", e)
            return self._hold(f"예측 오류: {e}")

    def _hold(self, note: str) -> MLPrediction:
        return MLPrediction(
            action="HOLD", confidence=0.0,
            proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
            model_name=self._model_name,
            note=note,
        )
