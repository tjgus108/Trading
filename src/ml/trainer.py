"""
C1. WalkForwardTrainer: RandomForest walk-forward 학습.

학습 규칙:
  - Train/validation/test split: 60/20/20 (시계열 순서 유지)
  - Walk-forward: 미래 데이터 누출 금지
  - 최소 성과: test accuracy > 55%
  - 모델 파일: models/<name>_<date>.pkl

사용법:
    trainer = WalkForwardTrainer(symbol="BTC/USDT")
    result = trainer.train(df)  # BacktestResult 유사 구조
    if result.passed:
        trainer.save("models/rf_btc_2024-01-01.pkl")
"""

import logging
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
MIN_ACCURACY = 0.55  # test accuracy 최소 기준


@dataclass
class TrainingResult:
    model_name: str
    n_samples: int
    n_features: int
    train_accuracy: float
    val_accuracy: float
    test_accuracy: float
    feature_importances: dict[str, float]
    passed: bool
    fail_reasons: list[str]
    model_path: Optional[str] = None

    def summary(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        lines = [
            f"ML_TRAINING_RESULT:",
            f"  model: {self.model_name}",
            f"  n_samples: {self.n_samples}",
            f"  train_accuracy: {self.train_accuracy:.3f}",
            f"  val_accuracy: {self.val_accuracy:.3f}",
            f"  test_accuracy: {self.test_accuracy:.3f}",
            f"  verdict: {verdict}",
        ]
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        if self.model_path:
            lines.append(f"  saved: {self.model_path}")
        # 상위 5개 피처 중요도
        top5 = sorted(self.feature_importances.items(), key=lambda x: x[1], reverse=True)[:5]
        if top5:
            lines.append("  top_features:")
            for fname, imp in top5:
                lines.append(f"    {fname}: {imp:.3f}")
        return "\n".join(lines)

    def feature_importance_report(self, top_n: int = 10) -> str:
        """
        피처 중요도 순위 보고서 반환.

        Args:
            top_n: 상위 N개 피처 출력 (기본 10)

        Returns:
            str: 순위별 피처명 + 중요도 + 누적 기여도
        """
        if not self.feature_importances:
            return "FEATURE_IMPORTANCE: (no data)"

        ranked = sorted(
            self.feature_importances.items(), key=lambda x: x[1], reverse=True
        )
        total = sum(v for _, v in ranked)
        cutoff = min(top_n, len(ranked))
        lines = [f"FEATURE_IMPORTANCE_REPORT (top {cutoff} / {len(ranked)}):"]
        cumulative = 0.0
        for rank, (fname, imp) in enumerate(ranked[:cutoff], start=1):
            pct = imp / total * 100 if total > 0 else 0.0
            cumulative += pct
            lines.append(
                f"  {rank:2d}. {fname:<22s} {imp:.4f}  ({pct:5.1f}%)  cumul={cumulative:5.1f}%"
            )
        return "\n".join(lines)


class WalkForwardTrainer:
    """
    RandomForest walk-forward 학습기.

    train(df): DataFrame → TrainingResult
    학습 완료 후 save()로 모델 저장.
    """

    def __init__(
        self,
        symbol: str = "BTC/USDT",
        n_estimators: int = 100,
        max_depth: int = 6,
        forward_n: int = 5,
        threshold: float = 0.003,
    ):
        self.symbol = symbol
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.feature_builder = FeatureBuilder(forward_n=forward_n, threshold=threshold)
        self._trained_model = None
        self._class_order: Optional[list[int]] = None
        self._feature_names: list[str] = []

    def train(self, df: pd.DataFrame) -> TrainingResult:
        """
        walk-forward 학습 실행 (데이터 누출 방지).
        df: DataFeed.fetch() 반환 DataFrame (지표 포함, 최소 200 캔들 권장)

        중요: 전체 df로 피처 계산 후 시계열 분할 (shift(1) 기반 피처는 look-ahead 없음).
        이 방식으로 val/test 구간의 rolling warm-up NaN으로 인한 유효 샘플 손실 방지.
        """
        try:
            from sklearn.calibration import CalibratedClassifierCV
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import accuracy_score
        except ImportError:
            logger.error("scikit-learn 미설치: pip install scikit-learn")
            return TrainingResult(
                model_name="", n_samples=0, n_features=0,
                train_accuracy=0, val_accuracy=0, test_accuracy=0,
                feature_importances={}, passed=False,
                fail_reasons=["scikit-learn not installed"],
            )

        # Walk-forward 분할 전략:
        # 피처를 전체 df로 계산한 후 시계열 순서대로 분할.
        # 이유: 모든 rolling/ewm 피처는 shift(1) 기반 → 현재 바 미래 데이터 누출 없음.
        # 반면 분할 후 각 구간에서 피처 계산 시 val/test 구간 앞부분의
        # rolling warm-up NaN으로 유효 샘플이 크게 줄어드는 문제 방지.
        X_all, y_all = self.feature_builder.build(df)

        n_total = len(X_all)
        train_end = int(n_total * 0.60)
        val_end = int(n_total * 0.80)

        X_train = X_all.iloc[:train_end]
        y_train = y_all.iloc[:train_end]
        X_val = X_all.iloc[train_end:val_end]
        y_val = y_all.iloc[train_end:val_end]
        X_test = X_all.iloc[val_end:]
        y_test = y_all.iloc[val_end:]

        logger.info(
            "Walk-forward split: n_total=%d train=%d val=%d test=%d",
            n_total, len(X_train), len(X_val), len(X_test),
        )

        n = len(X_train) + len(X_val) + len(X_test)
        
        if n < 100:
            return TrainingResult(
                model_name="", n_samples=n, n_features=X_train.shape[1] if len(X_train) > 0 else 0,
                train_accuracy=0, val_accuracy=0, test_accuracy=0,
                feature_importances={}, passed=False,
                fail_reasons=[f"샘플 부족: {n} < 100"],
            )

        logger.info(
            "Training RF: n_train=%d n_val=%d n_test=%d features=%d",
            len(X_train), len(X_val), len(X_test), X_train.shape[1] if len(X_train) > 0 else 0,
        )

        # 학습
        base_clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=42,
            n_jobs=-1,
            class_weight="balanced",
        )
        base_clf.fit(X_train, y_train)

        # Calibration: validation set으로 isotonic regression 적용
        # RF predict_proba는 과신(overconfident) 경향 → calibration으로 보정
        # method="isotonic" (비모수적, val set 크기 충분할 때 선호)
        # cv="prefit": base_clf가 이미 학습된 상태 → val set만 calibration에 사용
        clf = CalibratedClassifierCV(base_clf, method="isotonic", cv="prefit")
        clf.fit(X_val, y_val)

        # 성과 평가 (calibrated 모델 기준)
        train_acc = float(accuracy_score(y_train, clf.predict(X_train)))
        val_acc = float(accuracy_score(y_val, clf.predict(X_val)))
        test_acc = float(accuracy_score(y_test, clf.predict(X_test)))

        # 피처 중요도 (base estimator에서 추출)
        feat_importance = dict(zip(X_train.columns, base_clf.feature_importances_))

        fail_reasons = []
        if test_acc < MIN_ACCURACY:
            fail_reasons.append(f"test_accuracy {test_acc:.3f} < {MIN_ACCURACY}")
        if val_acc < MIN_ACCURACY:
            fail_reasons.append(f"val_accuracy {val_acc:.3f} < {MIN_ACCURACY}")

        self._trained_model = clf
        self._class_order = list(base_clf.classes_)
        self._feature_names = list(X_train.columns)
        model_name = f"rf_{self.symbol.replace('/', '').lower()}_{date.today()}"

        result = TrainingResult(
            model_name=model_name,
            n_samples=n,
            n_features=X_train.shape[1],
            train_accuracy=round(train_acc, 4),
            val_accuracy=round(val_acc, 4),
            test_accuracy=round(test_acc, 4),
            feature_importances=feat_importance,
            passed=len(fail_reasons) == 0,
            fail_reasons=fail_reasons,
        )
        logger.info(result.summary())
        logger.info(result.feature_importance_report())
        return result

    def get_feature_importances(self, top_n: Optional[int] = None) -> list[tuple[str, float]]:
        """
        학습된 모델의 피처 중요도를 내림차순으로 반환.

        Args:
            top_n: 상위 N개만 반환. None이면 전체.

        Returns:
            list of (feature_name, importance) �ples, 내림차순.

        Raises:
            RuntimeError: 모델이 학습되지 않은 경우.
        """
        if self._trained_model is None:
            raise RuntimeError("모델이 학습되지 않음 — train() 먼저 호출")

        # CalibratedClassifierCV는 feature_importances_ 없음 → base estimator에서 추출
        base = getattr(self._trained_model, "estimator", self._trained_model)
        importances = base.feature_importances_
        names = getattr(self, "_feature_names", [f"f{i}" for i in range(len(importances))])
        ranked = sorted(zip(names, importances), key=lambda x: x[1], reverse=True)
        if top_n is not None:
            ranked = ranked[:top_n]
        return ranked

    def save(self, path: Optional[str] = None) -> str:
        """학습된 모델을 pkl로 저장. path 없으면 자동 생성."""
        if self._trained_model is None:
            raise RuntimeError("모델이 학습되지 않음 — train() 먼저 호출")

        MODELS_DIR.mkdir(exist_ok=True)
        if path is None:
            name = f"rf_{self.symbol.replace('/', '').lower()}_{date.today()}.pkl"
            path = str(MODELS_DIR / name)

        payload = {
            "model": self._trained_model,
            "name": Path(path).stem,
            "class_order": self._class_order,
            "symbol": self.symbol,
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        logger.info("ML model saved: %s", path)
        return path
