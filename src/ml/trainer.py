"""
C1. WalkForwardTrainer: RandomForest walk-forward 학습.

학습 규칙:
  - Train/val/calibration/test split: 60/15/15/10 (시계열 순서 유지)
  - Walk-forward: 미래 데이터 누출 금지
  - val_acc: base_clf로 val set 평가 (calibration 전)
  - calibration: 별도 calibration set으로 isotonic regression 적용
  - test_acc: calibrated 모델로 test set 최종 평가
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
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.ml.features import FeatureBuilder, RegimeAwareFeatureBuilder, detect_regime

# XGBoost optional import — 없으면 RF 단독 유지
try:
    import xgboost as xgb  # noqa: F401
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False

# SHAP optional import — 없으면 feature_importances_ fallback
try:
    import shap as _shap  # noqa: F401
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False

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
    feature_importances: Dict[str, float]
    passed: bool
    fail_reasons: List[str]
    model_path: Optional[str] = None
    # Walk-forward 구간 정보 (선택)
    split_info: Optional[dict] = None
    # 클래스별 분포 (선택)
    class_distribution: Optional[dict] = None
    # Validation 성능 기반 앙상블 가중치
    ensemble_weight: float = 0.0
    # SHAP/importance 기반 선택된 피처 목록 (선택)
    selected_features: Optional[List[str]] = None
    # 레짐 감지 결과 (regime_aware=True 시)
    detected_regime: Optional[str] = None

    def summary(self) -> str:
        verdict = "PASS" if self.passed else "FAIL"
        lines = [
            f"ML_TRAINING_RESULT:",
            f"  model: {self.model_name}",
            f"  n_samples: {self.n_samples}",
            f"  train_accuracy: {self.train_accuracy:.3f}",
            f"  val_accuracy: {self.val_accuracy:.3f}",
            f"  test_accuracy: {self.test_accuracy:.3f}",
            f"  ensemble_weight: {self.ensemble_weight:.4f}",
            f"  verdict: {verdict}",
        ]
        if self.detected_regime:
            lines.append(f"  detected_regime: {self.detected_regime}")
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        if self.model_path:
            lines.append(f"  saved: {self.model_path}")
        # Walk-forward 구간 정보
        if self.split_info:
            split_parts = (
                f"  split: train={self.split_info.get('n_train')} "
                f"val={self.split_info.get('n_val')} "
            )
            if "n_cal" in self.split_info:
                split_parts += f"cal={self.split_info.get('n_cal')} "
            split_parts += f"test={self.split_info.get('n_test')}"
            lines.append(split_parts)
        # 클래스별 분포
        if self.class_distribution:
            dist_str = "  ".join(
                f"{k}={v:.1%}" for k, v in sorted(self.class_distribution.items())
            )
            lines.append(f"  class_dist: {dist_str}")
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
        binary: bool = False,
        triple_barrier: bool = False,
        tb_tp_pct: float = 0.02,
        tb_sl_pct: float = 0.01,
        ensemble: bool = True,
        model_type: str = "rf",
        use_shap_selection: bool = False,
        regime_aware: bool = False,
    ):
        self.symbol = symbol
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.binary = binary
        self.triple_barrier = triple_barrier
        self.ensemble = ensemble  # XGBoost 앙상블 사용 여부 (XGBoost 미설치 시 자동 비활성)
        # model_type: "rf" | "extra_trees" | "xgboost"
        # xgboost 선택 시 미설치면 rf로 fallback
        if model_type == "xgboost" and not _XGB_AVAILABLE:
            logger.warning("xgboost 미설치 — model_type='rf'로 fallback")
            self.model_type = "rf"
        else:
            self.model_type = model_type
        self.use_shap_selection = use_shap_selection  # SHAP/importance 기반 피처 선택
        self.regime_aware = regime_aware  # 레짐별 동적 피처 선택 활성화
        fb_kwargs = dict(
            forward_n=forward_n, threshold=threshold,
            binary=binary,
            triple_barrier=triple_barrier,
            tb_tp_pct=tb_tp_pct,
            tb_sl_pct=tb_sl_pct,
        )
        if regime_aware:
            self.feature_builder = RegimeAwareFeatureBuilder(**fb_kwargs)
        else:
            self.feature_builder = FeatureBuilder(**fb_kwargs)
        self._trained_model = None
        self._class_order: Optional[List[int]] = None
        self._feature_names: List[str] = []
        self._last_feature_importances: Dict[str, float] = {}
        self._trained_regime: Optional[str] = None  # 학습 시 감지된 레짐

    def train(self, df: pd.DataFrame) -> TrainingResult:
        """
        walk-forward 학습 실행 (데이터 누출 방지).
        df: DataFeed.fetch() 반환 DataFrame (지표 포함, 최소 200 캔들 권장)

        중요: 전체 df로 피처 계산 후 시계열 분할 (shift(1) 기반 피처는 look-ahead 없음).
        이 방식으로 val/test 구간의 rolling warm-up NaN으로 인한 유효 샘플 손실 방지.
        """
        try:
            from sklearn.calibration import CalibratedClassifierCV
            from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, VotingClassifier
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

        # 레짐별 동적 피처 선택 (regime_aware=True 시)
        if self.regime_aware and isinstance(self.feature_builder, RegimeAwareFeatureBuilder):
            X_all, y_all, regime = self.feature_builder.build_with_regime(df)
            self._trained_regime = regime
            logger.info("레짐 감지: %s → 피처 수=%d", regime, X_all.shape[1])
        else:
            X_all, y_all = self.feature_builder.build(df)
            self._trained_regime = None
        # Int64 (nullable) → int64: sklearn 호환성 보장
        y_all = y_all.astype(int)

        n_total = len(X_all)
        train_end = int(n_total * 0.60)
        val_end = int(n_total * 0.75)
        cal_end = int(n_total * 0.90)

        X_train = X_all.iloc[:train_end]
        y_train = y_all.iloc[:train_end]
        X_val = X_all.iloc[train_end:val_end]
        y_val = y_all.iloc[train_end:val_end]
        X_cal = X_all.iloc[val_end:cal_end]
        y_cal = y_all.iloc[val_end:cal_end]
        X_test = X_all.iloc[cal_end:]
        y_test = y_all.iloc[cal_end:]

        split_info = {
            "n_total": n_total,
            "n_train": len(X_train),
            "n_val": len(X_val),
            "n_cal": len(X_cal),
            "n_test": len(X_test),
        }
        logger.info(
            "Walk-forward split: n_total=%d train=%d val=%d cal=%d test=%d",
            n_total, len(X_train), len(X_val), len(X_cal), len(X_test),
        )

        n = len(X_train) + len(X_val) + len(X_cal) + len(X_test)
        
        if n < 100:
            return TrainingResult(
                model_name="", n_samples=n, n_features=X_train.shape[1] if len(X_train) > 0 else 0,
                train_accuracy=0, val_accuracy=0, test_accuracy=0,
                feature_importances={}, passed=False,
                fail_reasons=[f"샘플 부족: {n} < 100"],
            )

        logger.info(
            "Training RF: n_train=%d n_val=%d n_cal=%d n_test=%d features=%d",
            len(X_train), len(X_val), len(X_cal), len(X_test),
            X_train.shape[1] if len(X_train) > 0 else 0,
        )

        # 학습
        # max_features='sqrt': 앙상블 다양성 확보 (기본값 'auto'='sqrt'이지만 명시)
        # max_depth=6: 과적합 방지 (기본 None에서 제한)
        if self.model_type == "xgboost" and _XGB_AVAILABLE:
            # XGBoost: gradient boosting — RF/ET와 다른 하이퍼파라미터 체계
            n_classes = len(np.unique(y_train))
            xgb_objective = "binary:logistic" if n_classes <= 2 else "multi:softprob"
            xgb_kwargs = dict(
                n_estimators=self.n_estimators,
                max_depth=3,  # boosting은 shallow tree 권장
                learning_rate=0.03,
                subsample=0.7,
                min_child_weight=3,
                reg_alpha=0.1,
                reg_lambda=1.0,
                objective=xgb_objective,
                random_state=42,
                n_jobs=-1,
                use_label_encoder=False,
                eval_metric="mlogloss" if n_classes > 2 else "logloss",
            )
            if n_classes > 2:
                xgb_kwargs["num_class"] = n_classes
            base_clf = xgb.XGBClassifier(**xgb_kwargs)
            # early_stopping: eval_set으로 과적합 방지
            base_clf.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
        else:
            clf_kwargs = dict(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                max_features="sqrt",
                min_samples_leaf=max(10, len(X_train) // 20),
                min_samples_split=20,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            )
            if self.model_type == "extra_trees":
                base_clf = ExtraTreesClassifier(**clf_kwargs)
            else:
                base_clf = RandomForestClassifier(**clf_kwargs)
            base_clf.fit(X_train, y_train)

        # --- SHAP/importance 기반 피처 선택 (optional) ---
        selected_features: Optional[List[str]] = None
        if self.use_shap_selection:
            feat_imp_arr = base_clf.feature_importances_
            feat_names = list(X_train.columns)
            total_imp = feat_imp_arr.sum()

            if _SHAP_AVAILABLE and total_imp > 0:
                try:
                    import shap
                    explainer = shap.TreeExplainer(base_clf)
                    shap_values = explainer.shap_values(X_train)
                    # multi-class: shap_values is list → mean abs across classes
                    if isinstance(shap_values, list):
                        shap_imp = np.mean(
                            [np.abs(sv).mean(axis=0) for sv in shap_values], axis=0
                        )
                    else:
                        shap_imp = np.abs(shap_values).mean(axis=0)
                    imp_source = shap_imp / shap_imp.sum() if shap_imp.sum() > 0 else feat_imp_arr / (total_imp or 1)
                    logger.info("SHAP 기반 피처 선택 사용")
                except Exception as e:
                    logger.warning("SHAP 계산 실패, feature_importances_ fallback: %s", e)
                    imp_source = feat_imp_arr / (total_imp or 1)
            else:
                imp_source = feat_imp_arr / (total_imp or 1)
                if not _SHAP_AVAILABLE:
                    logger.info("shap 미설치 — feature_importances_ fallback으로 피처 선택")

            threshold_imp = 0.05  # 전체 importance의 5% 미만 제거
            mask = imp_source >= threshold_imp
            selected_features = [f for f, keep in zip(feat_names, mask) if keep]

            if len(selected_features) < 2:
                # 최소 2개 피처 보장
                logger.warning("SHAP 선택 후 피처 수 < 2 — 선택 취소")
                selected_features = feat_names
            elif len(selected_features) < len(feat_names):
                removed = [f for f, keep in zip(feat_names, mask) if not keep]
                logger.info(
                    "피처 선택: %d→%d (제거: %s)",
                    len(feat_names), len(selected_features), removed,
                )
                # 선택된 피처로 재학습
                X_train = X_train[selected_features]
                X_val = X_val[selected_features]
                X_cal = X_cal[selected_features]
                X_test = X_test[selected_features]

                if self.model_type == "xgboost" and _XGB_AVAILABLE:
                    base_clf = xgb.XGBClassifier(**xgb_kwargs)
                    base_clf.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        verbose=False,
                    )
                else:
                    clf_kwargs["min_samples_leaf"] = max(10, len(X_train) // 20)
                    if self.model_type == "extra_trees":
                        base_clf = ExtraTreesClassifier(**clf_kwargs)
                    else:
                        base_clf = RandomForestClassifier(**clf_kwargs)
                    base_clf.fit(X_train, y_train)
            else:
                logger.info("SHAP 선택: 모든 피처 유지 (%d개)", len(selected_features))

        # val_acc는 calibration 전 base 모델로 평가 (누출 방지)
        train_acc = float(accuracy_score(y_train, base_clf.predict(X_train)))
        val_acc = float(accuracy_score(y_val, base_clf.predict(X_val)))

        # Calibration: 별도 calibration set으로 isotonic regression 적용 (val 누출 방지)
        try:
            clf = CalibratedClassifierCV(base_clf, method="isotonic", cv="prefit")
            clf.fit(X_cal, y_cal)
        except (TypeError, Exception):
            clf = base_clf

        # test_acc는 calibrated 모델로 평가
        test_acc = float(accuracy_score(y_test, clf.predict(X_test)))

        # 피처 중요도 (base estimator에서 추출)
        feat_importance = dict(zip(X_train.columns, base_clf.feature_importances_))

        # 클래스별 분포 (전체 구간 기준)
        y_all_concat = pd.concat([y_train, y_val, y_cal, y_test])
        total_labels = len(y_all_concat)
        class_distribution = {
            str(cls): (y_all_concat == cls).sum() / total_labels
            for cls in sorted(y_all_concat.unique())
        }

        fail_reasons = []
        if test_acc < MIN_ACCURACY:
            fail_reasons.append(f"test_accuracy {test_acc:.3f} < {MIN_ACCURACY}")
        if val_acc < MIN_ACCURACY:
            fail_reasons.append(f"val_accuracy {val_acc:.3f} < {MIN_ACCURACY}")

        # 앙상블 가중치: val + test 평균 성능에서 기준선(0.5) 초과분 기반
        # 범위 [0, 1], PASS 기준 미달 시 0으로 패널티
        raw_weight = (val_acc + test_acc) / 2.0 - 0.50
        ensemble_weight = round(max(0.0, raw_weight), 4) if len(fail_reasons) == 0 else 0.0

        self._trained_model = clf
        self._class_order = list(base_clf.classes_)
        self._feature_names = list(X_train.columns)
        self._last_feature_importances = feat_importance
        label_mode = "tb" if self.triple_barrier else ("binary" if self.binary else "3class")
        algo_tag = "xgb" if self.model_type == "xgboost" else ("et" if self.model_type == "extra_trees" else "rf")
        model_name = f"{algo_tag}_{self.symbol.replace('/', '').lower()}_{label_mode}_{date.today()}"

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
            split_info=split_info,
            class_distribution=class_distribution,
            ensemble_weight=ensemble_weight,
            selected_features=selected_features,
            detected_regime=self._trained_regime,
        )
        logger.info(result.summary())
        logger.info(result.feature_importance_report())
        return result

    def get_feature_importances(self, top_n: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        학습된 모델의 피처 중요도를 내림차순으로 반환.

        Args:
            top_n: 상위 N개만 반환. None이면 전체.

        Returns:
            list of (feature_name, importance) tuples, 내림차순.

        Raises:
            RuntimeError: 모델이 학습되지 않은 경우.
        """
        if self._trained_model is None:
            raise RuntimeError("모델이 학습되지 않음 — train() 먼저 호출")

        # 캐시된 피처 중요도 우선 사용
        if self._last_feature_importances:
            ranked = sorted(
                self._last_feature_importances.items(),
                key=lambda x: x[1], reverse=True,
            )
            if top_n is not None:
                ranked = ranked[:top_n]
            return ranked

        # fallback: base estimator에서 추출
        # CalibratedClassifierCV: sklearn <1.2 → base_estimator, >=1.2 → estimator
        base = getattr(
            self._trained_model, "estimator",
            getattr(self._trained_model, "base_estimator", self._trained_model),
        )
        importances = base.feature_importances_
        names = getattr(self, "_feature_names", [f"f{i}" for i in range(len(importances))])
        ranked = sorted(zip(names, importances), key=lambda x: x[1], reverse=True)
        if top_n is not None:
            ranked = ranked[:top_n]
        return ranked

    def compute_ensemble_weight(
        self,
        results: List["TrainingResult"],
        baseline: float = 0.50,
    ) -> List[float]:
        """
        여러 TrainingResult로부터 validation 성능 기반 정규화된 앙상블 가중치 계산.

        각 모델의 가중치 = (val_acc + test_acc) / 2 - baseline (음수 → 0 클리핑).
        전체 합이 1이 되도록 정규화. PASS 모델만 가중치 부여.

        Args:
            results: TrainingResult 리스트 (복수 모델 비교 시 활용)
            baseline: 기준 정확도 (기본 0.50 = 랜덤 수준)

        Returns:
            List[float]: 각 모델의 정규화 가중치 (합=1.0, 또는 전부 0이면 균등 분배)

        Example:
            r1 = trainer1.train(df1)
            r2 = trainer2.train(df2)
            weights = trainer1.compute_ensemble_weight([r1, r2])
            # → [0.6, 0.4] 등
        """
        raw = []
        for r in results:
            if not r.passed:
                raw.append(0.0)
            else:
                score = (r.val_accuracy + r.test_accuracy) / 2.0 - baseline
                raw.append(max(0.0, score))

        total = sum(raw)
        if total <= 0.0:
            # 모두 FAIL이면 균등 분배
            n = len(results)
            return [1.0 / n if n > 0 else 0.0] * n
        return [round(w / total, 6) for w in raw]

    def compute_ensemble_weight_recency(
        self,
        results: List["TrainingResult"],
        baseline: float = 0.50,
        decay: float = 0.85,
    ) -> List[float]:
        """
        시간 순서를 반영한 앙상블 가중치 계산.

        리스트의 뒤쪽(최신) 모델에 더 높은 가중치를 부여.
        decay=0.85이면 한 단계 이전 모델은 85%만큼 가중치 감소.

        Args:
            results: TrainingResult 리스트 (시간 순서: 오래된→최신)
            baseline: 기준 정확도 (기본 0.50)
            decay: 시간 감쇠율 (0~1). 1이면 감쇠 없음.

        Returns:
            List[float]: 정규화 가중치 (합=1.0)
        """
        n = len(results)
        if n == 0:
            return []

        raw = []
        for i, r in enumerate(results):
            if not r.passed:
                raw.append(0.0)
                continue
            perf = (r.val_accuracy + r.test_accuracy) / 2.0 - baseline
            perf = max(0.0, perf)
            # 시간 가중치: 마지막(최신)이 가장 큼
            time_weight = decay ** (n - 1 - i)
            raw.append(perf * time_weight)

        total = sum(raw)
        if total <= 0.0:
            return [1.0 / n] * n
        return [round(w / total, 6) for w in raw]

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
            "feature_names": self._feature_names,
            "feature_importances": self._last_feature_importances,
            "train_date": str(date.today()),
            "trained_regime": self._trained_regime,
        }
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        logger.info("ML model saved: %s", path)
        return path


class MultiWindowEnsemble:
    """
    다시간 앙상블 stacking: 30/60/90일 윈도우에 RF/ExtraTrees/XGBoost 할당.

    - softmax 동적 가중치 (temperature=1.5)
    - 초기 20거래 균등 가중치, rolling 20거래마다 갱신
    - predict_proba → 가중 평균 → BUY/SELL/HOLD
    """

    WINDOWS = [30, 60, 90]
    DEFAULT_MODEL_TYPES = ["rf", "extra_trees", "xgboost"]

    def __init__(
        self,
        symbol: str = "BTC/USDT",
        temperature: float = 1.5,
        update_every: int = 20,
        n_estimators: int = 100,
        forward_n: int = 5,
        threshold: float = 0.003,
    ):
        self.symbol = symbol
        self.temperature = temperature
        self.update_every = update_every
        self.n_estimators = n_estimators
        self.forward_n = forward_n
        self.threshold = threshold

        # 각 윈도우별 WalkForwardTrainer
        self._trainers: List[WalkForwardTrainer] = []
        # 가중치 (uniform until first update)
        self._weights: np.ndarray = np.ones(3) / 3.0
        # rolling 성능 누적 (val+test acc)
        self._rolling_accs: List[List[float]] = [[], [], []]
        self._trade_count: int = 0
        self._last_results: List[Optional[TrainingResult]] = [None, None, None]

        # 윈도우별 모델 타입 결정 (xgboost 미설치 시 fallback)
        model_types = list(self.DEFAULT_MODEL_TYPES)
        if not _XGB_AVAILABLE:
            model_types[2] = "rf"
            logger.warning("xgboost 미설치 — 90일 윈도우 model_type='rf'로 fallback")

        for mtype in model_types:
            self._trainers.append(
                WalkForwardTrainer(
                    symbol=symbol,
                    n_estimators=n_estimators,
                    forward_n=forward_n,
                    threshold=threshold,
                    model_type=mtype,
                )
            )

    def train(self, df: pd.DataFrame) -> List[TrainingResult]:
        """
        각 윈도우(30/60/90일)로 슬라이싱 후 독립 학습.
        df는 최소 90일치 이상 캔들 필요 (시간봉 기준 90*24=2160 캔들 이상 권장).
        """
        results = []
        window_sizes_rows = [self.WINDOWS[i] * 24 for i in range(3)]  # 시간봉 기준

        for i, (trainer, nrows) in enumerate(zip(self._trainers, window_sizes_rows)):
            if len(df) < nrows:
                # 데이터 부족 → 전체 df 사용
                df_window = df
                logger.warning(
                    "윈도우 %d일: 데이터 부족 (%d < %d) — 전체 df 사용",
                    self.WINDOWS[i], len(df), nrows,
                )
            else:
                df_window = df.iloc[-nrows:]

            result = trainer.train(df_window)
            results.append(result)
            self._last_results[i] = result
            if result.passed:
                self._rolling_accs[i].append(
                    (result.val_accuracy + result.test_accuracy) / 2.0
                )

        self._update_weights()
        return results

    def _softmax_weights(self, scores: np.ndarray) -> np.ndarray:
        """softmax with temperature scaling."""
        scaled = scores / self.temperature
        shifted = scaled - scaled.max()  # numerical stability
        exp_s = np.exp(shifted)
        return exp_s / exp_s.sum()

    def _update_weights(self) -> None:
        """rolling 평균 성능 기반 softmax 가중치 갱신."""
        scores = []
        for accs in self._rolling_accs:
            if len(accs) == 0:
                scores.append(0.5)  # neutral
            else:
                recent = accs[-self.update_every :]
                scores.append(float(np.mean(recent)))

        scores_arr = np.array(scores, dtype=float)
        self._weights = self._softmax_weights(scores_arr)
        logger.info(
            "MultiWindowEnsemble 가중치 갱신: w30=%.3f w60=%.3f w90=%.3f",
            *self._weights,
        )

    def predict(self, df: pd.DataFrame) -> dict:
        """
        세 모델의 predict_proba를 가중 평균하여 BUY/SELL/HOLD 반환.

        Returns:
            dict with keys: action, confidence, proba_buy, proba_sell, proba_hold,
                           weights, model
        """
        trained = [t for t in self._trainers if t._trained_model is not None]
        if not trained:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "proba_buy": 0.0,
                "proba_sell": 0.0,
                "proba_hold": 1.0,
                "weights": self._weights.tolist(),
                "model": "MultiWindowEnsemble",
                "note": "no model trained",
            }

        # 각 모델에서 predict_proba 계산 후 가중 평균
        probas = []  # shape: (n_trained, 3) — [buy, sell, hold]
        active_weights = []

        for i, trainer in enumerate(self._trainers):
            if trainer._trained_model is None:
                continue

            # 피처 빌드
            fb = trainer.feature_builder
            try:
                feat = fb.build_features_only(df)
                if trainer._feature_names:
                    feat = feat.reindex(columns=trainer._feature_names, fill_value=0.0)
                X_live = feat.iloc[[-1]]
            except Exception as e:
                logger.warning("MultiWindowEnsemble 피처 빌드 실패 (윈도우 %d): %s", self.WINDOWS[i], e)
                continue

            try:
                proba_raw = trainer._trained_model.predict_proba(X_live)[0]
            except Exception as e:
                logger.warning("MultiWindowEnsemble predict_proba 실패 (윈도우 %d): %s", self.WINDOWS[i], e)
                continue

            # class_order → [buy=1, sell=-1, hold=0] 순으로 정렬
            class_order = trainer._class_order or []
            proba_map = dict(zip(class_order, proba_raw))
            p_buy = float(proba_map.get(1, proba_map.get(1.0, 0.0)))
            p_sell = float(proba_map.get(-1, proba_map.get(-1.0, 0.0)))
            p_hold = float(proba_map.get(0, proba_map.get(0.0, 0.0)))

            total_p = p_buy + p_sell + p_hold
            if total_p > 0:
                p_buy /= total_p
                p_sell /= total_p
                p_hold /= total_p

            probas.append([p_buy, p_sell, p_hold])
            active_weights.append(self._weights[i])

        if not probas:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "proba_buy": 0.0,
                "proba_sell": 0.0,
                "proba_hold": 1.0,
                "weights": self._weights.tolist(),
                "model": "MultiWindowEnsemble",
                "note": "prediction failed",
            }

        # 가중 평균
        w_arr = np.array(active_weights, dtype=float)
        w_arr = w_arr / w_arr.sum()
        probas_arr = np.array(probas)
        weighted = (probas_arr * w_arr[:, None]).sum(axis=0)

        p_buy, p_sell, p_hold = float(weighted[0]), float(weighted[1]), float(weighted[2])
        max_idx = int(np.argmax(weighted))
        actions = ["BUY", "SELL", "HOLD"]
        action = actions[max_idx]
        confidence = float(weighted[max_idx])

        # rolling 성능 누적 (거래 카운터 기반 갱신)
        self._trade_count += 1
        if self._trade_count % self.update_every == 0:
            self._update_weights()

        return {
            "action": action,
            "confidence": round(confidence, 4),
            "proba_buy": round(p_buy, 4),
            "proba_sell": round(p_sell, 4),
            "proba_hold": round(p_hold, 4),
            "weights": [round(float(w), 4) for w in self._weights],
            "model": f"MultiWindowEnsemble(30/60/90d)",
        }

    def update_performance(self, window_idx: int, accuracy: float) -> None:
        """
        외부에서 거래 결과 기반 성능 업데이트.

        Args:
            window_idx: 0=30일, 1=60일, 2=90일
            accuracy: 최근 거래 정확도 (0~1)
        """
        if 0 <= window_idx < 3:
            self._rolling_accs[window_idx].append(accuracy)
            logger.debug(
                "MultiWindowEnsemble 성능 업데이트: window=%d acc=%.3f",
                self.WINDOWS[window_idx], accuracy,
            )

    @property
    def weights(self) -> List[float]:
        return [round(float(w), 4) for w in self._weights]


def combinatorial_purged_cv(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 6,
    purge_gap: int = 5,
    embargo_pct: float = 0.01,
) -> List[Dict]:
    """
    Combinatorial Purged Cross-Validation (CPCV) — sklearn 기반 구현.

    skfolio CombinatorialPurgedCV의 핵심 아이디어를 sklearn TimeSeriesSplit으로 근사.
    미래 데이터 누출 방지를 위해 train/test 사이에 purge_gap 간격과
    embargo(테스트 끝 이후 일정 구간 제외)를 적용.

    Args:
        X: 피처 DataFrame (시계열 순서 필수)
        y: 레이블 Series
        n_splits: CV fold 수 (기본 6)
        purge_gap: train-test 경계 간 제거 샘플 수 (기본 5, forward_n과 동일 권장)
        embargo_pct: 테스트 끝 이후 embargo 비율 (기본 1%)

    Returns:
        List[Dict]: 각 fold의 결과
          - fold: fold 번호
          - n_train: train 샘플 수
          - n_test: test 샘플 수
          - train_acc: train accuracy
          - test_acc: test accuracy
          - purged_samples: purge로 제거된 샘플 수

    Example:
        fb = FeatureBuilder(binary=True, triple_barrier=True)
        X, y = fb.build(df)
        y = y.astype(int)
        results = combinatorial_purged_cv(X, y, n_splits=6, purge_gap=5)
        avg_test_acc = sum(r["test_acc"] for r in results) / len(results)
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import TimeSeriesSplit
    except ImportError:
        logger.error("scikit-learn 미설치")
        return []

    n = len(X)
    embargo_size = max(1, int(n * embargo_pct))
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=purge_gap)

    results = []
    for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X)):
        # Embargo: test set 이후 구간을 train에서 제거 (이미 gap으로 처리되지만 보강)
        # test 끝 이후 embargo_size 만큼 추가 제거
        test_end = test_idx[-1]
        embargo_end = min(n, test_end + embargo_size)

        # purge: train에서 test 시작 이전 purge_gap 구간 제거
        test_start = test_idx[0]
        purge_start = max(0, test_start - purge_gap)
        purged_mask = train_idx < purge_start
        train_idx_purged = train_idx[purged_mask]
        purged_count = len(train_idx) - len(train_idx_purged)

        if len(train_idx_purged) < 50 or len(test_idx) < 20:
            logger.debug("CPCV fold %d: 샘플 부족 (train=%d, test=%d) — 건너뜀",
                         fold_idx, len(train_idx_purged), len(test_idx))
            continue

        X_train = X.iloc[train_idx_purged]
        y_train = y.iloc[train_idx_purged]
        X_test = X.iloc[test_idx]
        y_test = y.iloc[test_idx]

        clf = RandomForestClassifier(
            n_estimators=50,
            max_depth=6,
            max_features="sqrt",
            random_state=42 + fold_idx,
            n_jobs=-1,
            class_weight="balanced",
        )
        clf.fit(X_train, y_train)

        train_acc = float(accuracy_score(y_train, clf.predict(X_train)))
        test_acc = float(accuracy_score(y_test, clf.predict(X_test)))

        fold_result = {
            "fold": fold_idx,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "train_acc": round(train_acc, 4),
            "test_acc": round(test_acc, 4),
            "purged_samples": purged_count,
        }
        results.append(fold_result)
        logger.info(
            "CPCV fold %d: train=%d test=%d purged=%d | train_acc=%.3f test_acc=%.3f",
            fold_idx, len(X_train), len(X_test), purged_count, train_acc, test_acc,
        )

    if results:
        avg_test = np.mean([r["test_acc"] for r in results])
        std_test = np.std([r["test_acc"] for r in results])
        logger.info(
            "CPCV summary: %d folds, avg_test_acc=%.3f ± %.3f",
            len(results), avg_test, std_test,
        )

    return results
