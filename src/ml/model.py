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
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.ml.features import FeatureBuilder

logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MIN_ACCURACY = 0.55  # 최소 정확도 기준


@dataclass
class MLPrediction:
    """단일 예측 결과 컨테이너. summary()로 표준 출력 포맷 생성."""

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
        self._label_map: Dict[int, str] = {1: "BUY", -1: "SELL", 0: "HOLD"}
        self._class_order: Optional[List[int]] = None  # 모델의 class 순서
        self._feature_importances: Dict[str, float] = {}
        self._train_date: Optional[str] = None
        # Inference latency tracking (벤치마크 유틸)
        self._latency_ms: List[float] = []

    def load(self, path: str) -> bool:
        """모델 파일 로드. 실패 시 False 반환."""
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            self._model = data["model"]
            self._model_name = data.get("name", Path(path).stem)
            self._class_order = data.get("class_order", [-1, 0, 1])
            self._feature_importances = data.get("feature_importances", {})
            self._train_date = data.get("train_date")
            if self._feature_importances:
                top3 = sorted(
                    self._feature_importances.items(),
                    key=lambda x: x[1], reverse=True,
                )[:3]
                top3_str = ", ".join(f"{n}={v:.3f}" for n, v in top3)
                logger.info("Top features: %s", top3_str)
            logger.info("ML model loaded: %s (trained: %s)", self._model_name, self._train_date or "unknown")
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
        추론 경과시간은 내부적으로 기록 (benchmark_stats()로 조회).
        """
        _t0 = time.perf_counter()
        try:
            if self._model is None:
                result = MLPrediction(
                    action="HOLD", confidence=0.0,
                    proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
                    model_name="no model trained",
                    note="모델 없음 — WalkForwardTrainer로 학습 필요",
                )
            else:
                feat_df = self.feature_builder.build_features_only(df)
                if feat_df.empty:
                    result = self._hold("피처 계산 실패")
                elif len(feat_df) < 2:
                    result = self._hold("피처 데이터 부족")
                else:
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

                    result = MLPrediction(
                        action=action,
                        confidence=confidence,
                        proba_buy=float(p_buy),
                        proba_sell=float(p_sell),
                        proba_hold=float(p_hold),
                        model_name=self._model_name,
                    )
        except Exception as e:
            logger.error("ML predict error: %s", e)
            result = self._hold(f"예측 오류: {e}")
        finally:
            elapsed_ms = (time.perf_counter() - _t0) * 1000.0
            self._latency_ms.append(elapsed_ms)
            logger.debug("ML predict latency: %.2f ms (model=%s)", elapsed_ms, self._model_name)

        return result

    # ------------------------------------------------------------------
    # Inference benchmark utilities
    # ------------------------------------------------------------------

    def benchmark_stats(self) -> Dict[str, float]:
        """
        누적 추론 지연시간 통계 반환 (단위: ms).

        Returns:
            dict with keys: count, mean_ms, p50_ms, p95_ms, p99_ms, max_ms
            샘플 없으면 모두 0.0.
        """
        if not self._latency_ms:
            return {"count": 0, "mean_ms": 0.0, "p50_ms": 0.0,
                    "p95_ms": 0.0, "p99_ms": 0.0, "max_ms": 0.0}
        arr = np.array(self._latency_ms)
        return {
            "count": len(arr),
            "mean_ms": float(np.mean(arr)),
            "p50_ms": float(np.percentile(arr, 50)),
            "p95_ms": float(np.percentile(arr, 95)),
            "p99_ms": float(np.percentile(arr, 99)),
            "max_ms": float(np.max(arr)),
        }

    def reset_benchmark(self) -> None:
        """누적 추론 지연시간 기록 초기화."""
        self._latency_ms = []

    def get_feature_importances(self, top_n: Optional[int] = None) -> List[tuple]:
        """
        로드된 모델의 피처 중요도 반환 (내림차순).

        Returns:
            list of (feature_name, importance). 모델 미로드 시 빈 리스트.
        """
        if not self._feature_importances:
            return []
        ranked = sorted(
            self._feature_importances.items(),
            key=lambda x: x[1], reverse=True,
        )
        if top_n is not None:
            ranked = ranked[:top_n]
        return ranked

    def get_low_importance_features(self, threshold: float = 0.01) -> List[str]:
        """중요도 threshold 미만인 피처 이름 반환 (모델 경량화/과적합 방지 목적).

        Args:
            threshold: 중요도 하한선. 이 값 미만인 피처는 제거 후보.

        Returns:
            낮은 중요도 피처 이름 리스트. 모델 미로드 시 빈 리스트.
        """
        return [name for name, imp in self._feature_importances.items() if imp < threshold]

    def _hold(self, note: str) -> MLPrediction:
        """note와 함께 HOLD 신호(confidence=0)를 반환하는 내부 헬퍼."""
        return MLPrediction(
            action="HOLD", confidence=0.0,
            proba_buy=0.0, proba_sell=0.0, proba_hold=1.0,
            model_name=self._model_name,
            note=note,
        )
