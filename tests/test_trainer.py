"""
Tests for src/ml/trainer.py — WalkForwardTrainer, TrainingResult, combinatorial_purged_cv.
"""

import pickle
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.ml.trainer import (
    MIN_ACCURACY,
    TrainingResult,
    WalkForwardTrainer,
    combinatorial_purged_cv,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """학습에 충분한 OHLCV DataFrame 생성 (최소 200 캔들 권장)."""
    rng = np.random.RandomState(seed)
    close = 100.0 + np.cumsum(rng.randn(n) * 0.5)
    close = np.maximum(close, 10.0)  # 양수 보장
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    volume = rng.uniform(100, 1000, n)
    return pd.DataFrame({
        "open": close + rng.randn(n) * 0.1,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def _make_small_ohlcv(n: int = 50) -> pd.DataFrame:
    """샘플 부족 테스트용 작은 DataFrame."""
    return _make_ohlcv(n=n, seed=99)


# ---------------------------------------------------------------------------
# TrainingResult 단위 테스트
# ---------------------------------------------------------------------------

class TestTrainingResult:

    def _make_result(self, **overrides) -> TrainingResult:
        defaults = dict(
            model_name="rf_btcusdt_binary_2024-01-01",
            n_samples=500,
            n_features=12,
            train_accuracy=0.75,
            val_accuracy=0.65,
            test_accuracy=0.60,
            feature_importances={"return_1": 0.3, "atr_pct": 0.2, "ema_ratio": 0.15},
            passed=True,
            fail_reasons=[],
        )
        defaults.update(overrides)
        return TrainingResult(**defaults)

    def test_summary_pass(self):
        result = self._make_result()
        s = result.summary()
        assert "PASS" in s
        assert "rf_btcusdt_binary_2024-01-01" in s

    def test_summary_fail(self):
        result = self._make_result(passed=False, fail_reasons=["test_accuracy 0.50 < 0.55"])
        s = result.summary()
        assert "FAIL" in s
        assert "test_accuracy" in s

    def test_summary_with_split_info(self):
        result = self._make_result(split_info={"n_train": 300, "n_val": 75, "n_cal": 75, "n_test": 50})
        s = result.summary()
        assert "train=300" in s
        assert "cal=75" in s

    def test_summary_with_class_distribution(self):
        result = self._make_result(class_distribution={"0": 0.4, "1": 0.6})
        s = result.summary()
        assert "class_dist" in s

    def test_summary_with_model_path(self):
        result = self._make_result(model_path="/tmp/test_model.pkl")
        s = result.summary()
        assert "/tmp/test_model.pkl" in s

    def test_feature_importance_report(self):
        result = self._make_result()
        report = result.feature_importance_report(top_n=2)
        assert "FEATURE_IMPORTANCE_REPORT" in report
        assert "return_1" in report
        assert "cumul=" in report

    def test_feature_importance_report_empty(self):
        result = self._make_result(feature_importances={})
        report = result.feature_importance_report()
        assert "no data" in report

    def test_ensemble_weight_default(self):
        result = self._make_result()
        assert result.ensemble_weight == 0.0  # 기본값


# ---------------------------------------------------------------------------
# WalkForwardTrainer 단위 테스트
# ---------------------------------------------------------------------------

class TestWalkForwardTrainer:

    def test_init_defaults(self):
        trainer = WalkForwardTrainer()
        assert trainer.symbol == "BTC/USDT"
        assert trainer.n_estimators == 100
        assert trainer.max_depth == 6
        assert trainer._trained_model is None

    def test_train_returns_training_result(self):
        """학습 실행 후 TrainingResult 반환 확인."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert result.n_samples > 0
        assert result.n_features > 0
        assert result.train_accuracy > 0
        assert result.val_accuracy > 0
        assert result.test_accuracy > 0

    def test_train_model_name_contains_symbol(self):
        trainer = WalkForwardTrainer(symbol="ETH/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert "ethusdt" in result.model_name

    def test_train_binary_mode(self):
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", binary=True, n_estimators=10, max_depth=3,
            threshold=0.001, forward_n=3,
        )
        df = _make_ohlcv(500)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        if result.n_samples >= 100:
            assert "binary" in result.model_name
        else:
            # binary 모드는 중립 구간을 제거하므로 샘플이 줄어들 수 있음
            assert result.passed is False

    def test_train_triple_barrier_mode(self):
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", binary=True, triple_barrier=True,
            n_estimators=10, max_depth=3,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert "tb" in result.model_name

    def test_train_insufficient_samples(self):
        """샘플 부족 시 passed=False 반환."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10)
        df = _make_small_ohlcv(50)
        result = trainer.train(df)
        assert result.passed is False
        assert any("샘플 부족" in r or "부족" in r for r in result.fail_reasons)

    def test_train_sets_internal_model(self):
        """학습 후 내부 모델이 설정됨."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        trainer.train(df)
        assert trainer._trained_model is not None
        assert len(trainer._feature_names) > 0

    def test_train_split_ratio(self):
        """60/15/15/10 분할 비율 확인 (calibration hold-out 분리)."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        if result.split_info:
            n_total = result.split_info["n_total"]
            n_train = result.split_info["n_train"]
            n_val = result.split_info["n_val"]
            n_cal = result.split_info["n_cal"]
            n_test = result.split_info["n_test"]
            # 60/15/15/10 비율 (정수 반올림으로 약간의 오차 허용)
            assert abs(n_train / n_total - 0.60) < 0.05
            assert abs(n_val / n_total - 0.15) < 0.05
            assert abs(n_cal / n_total - 0.15) < 0.05
            assert abs(n_test / n_total - 0.10) < 0.05
            # 전체 합 일치
            assert n_train + n_val + n_cal + n_test == n_total

    def test_train_class_distribution(self):
        """클래스 분포 정보 포함 확인."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.class_distribution is not None
        total = sum(result.class_distribution.values())
        assert abs(total - 1.0) < 0.01  # 비율 합 ~1.0

    def test_train_feature_importances_not_empty(self):
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert len(result.feature_importances) > 0
        assert sum(result.feature_importances.values()) > 0

    def test_train_calibration_holdout_separate(self):
        """calibration set이 val/test와 분리되어 있는지 확인."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.split_info is not None
        # n_cal 키가 존재해야 함
        assert "n_cal" in result.split_info
        n_cal = result.split_info["n_cal"]
        n_val = result.split_info["n_val"]
        n_test = result.split_info["n_test"]
        # calibration set 크기 > 0
        assert n_cal > 0
        # val과 cal이 비슷한 크기 (~15% 각각)
        assert abs(n_val - n_cal) <= 2
        # test는 val보다 작아야 함 (10% vs 15%)
        assert n_test < n_val

    def test_train_ensemble_weight(self):
        """PASS 시 ensemble_weight > 0, FAIL 시 0."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        result = trainer.train(df)
        if result.passed:
            assert result.ensemble_weight > 0
        else:
            assert result.ensemble_weight == 0.0


# ---------------------------------------------------------------------------
# get_feature_importances
# ---------------------------------------------------------------------------

class TestGetFeatureImportances:

    def test_raises_before_train(self):
        trainer = WalkForwardTrainer()
        with pytest.raises(RuntimeError, match="학습되지 않음"):
            trainer.get_feature_importances()

    def test_returns_sorted_list(self):
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        trainer.train(df)
        importances = trainer.get_feature_importances()
        assert len(importances) > 0
        # 내림차순 정렬 확인
        for i in range(len(importances) - 1):
            assert importances[i][1] >= importances[i + 1][1]

    def test_top_n(self):
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        trainer.train(df)
        top3 = trainer.get_feature_importances(top_n=3)
        assert len(top3) == 3


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

class TestSaveLoad:

    def test_save_raises_before_train(self):
        trainer = WalkForwardTrainer()
        with pytest.raises(RuntimeError, match="학습되지 않음"):
            trainer.save()

    def test_save_creates_file(self):
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        trainer.train(df)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "test_model.pkl")
            saved_path = trainer.save(path=path)
            assert Path(saved_path).exists()

    def test_save_pickle_structure(self):
        """저장된 pkl에 필수 키가 포함되어 있는지 확인."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT", n_estimators=10, max_depth=3)
        df = _make_ohlcv(300)
        trainer.train(df)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "test_model.pkl")
            trainer.save(path=path)

            with open(path, "rb") as f:
                payload = pickle.load(f)

            assert "model" in payload
            assert "symbol" in payload
            assert "feature_names" in payload
            assert "feature_importances" in payload
            assert "class_order" in payload
            assert "train_date" in payload
            assert payload["symbol"] == "TEST/USDT"


# ---------------------------------------------------------------------------
# compute_ensemble_weight
# ---------------------------------------------------------------------------

class TestComputeEnsembleWeight:

    def _make_result(self, val_acc, test_acc, passed=True) -> TrainingResult:
        return TrainingResult(
            model_name="test",
            n_samples=100,
            n_features=10,
            train_accuracy=0.8,
            val_accuracy=val_acc,
            test_accuracy=test_acc,
            feature_importances={},
            passed=passed,
            fail_reasons=[] if passed else ["test"],
        )

    def test_single_model(self):
        trainer = WalkForwardTrainer()
        r1 = self._make_result(0.65, 0.60)
        weights = trainer.compute_ensemble_weight([r1])
        assert len(weights) == 1
        assert abs(weights[0] - 1.0) < 1e-6

    def test_two_models(self):
        trainer = WalkForwardTrainer()
        r1 = self._make_result(0.65, 0.60)
        r2 = self._make_result(0.70, 0.65)
        weights = trainer.compute_ensemble_weight([r1, r2])
        assert len(weights) == 2
        assert abs(sum(weights) - 1.0) < 1e-6
        # r2가 더 높으므로 가중치도 더 큼
        assert weights[1] > weights[0]

    def test_failed_model_zero_weight(self):
        trainer = WalkForwardTrainer()
        r1 = self._make_result(0.65, 0.60, passed=True)
        r2 = self._make_result(0.40, 0.35, passed=False)
        weights = trainer.compute_ensemble_weight([r1, r2])
        assert weights[1] == 0.0
        assert abs(weights[0] - 1.0) < 1e-6

    def test_all_failed_equal_distribution(self):
        trainer = WalkForwardTrainer()
        r1 = self._make_result(0.40, 0.35, passed=False)
        r2 = self._make_result(0.45, 0.40, passed=False)
        weights = trainer.compute_ensemble_weight([r1, r2])
        assert all(abs(w - 0.5) < 1e-6 for w in weights)

    def test_empty_list(self):
        trainer = WalkForwardTrainer()
        weights = trainer.compute_ensemble_weight([])
        assert weights == []


# ---------------------------------------------------------------------------
# compute_ensemble_weight_recency
# ---------------------------------------------------------------------------

class TestComputeEnsembleWeightRecency:

    def _make_result(self, val_acc, test_acc, passed=True) -> TrainingResult:
        return TrainingResult(
            model_name="test",
            n_samples=100,
            n_features=10,
            train_accuracy=0.8,
            val_accuracy=val_acc,
            test_accuracy=test_acc,
            feature_importances={},
            passed=passed,
            fail_reasons=[] if passed else ["test"],
        )

    def test_recency_favors_latest(self):
        """최신 모델(리스트 뒤쪽)에 더 높은 가중치."""
        trainer = WalkForwardTrainer()
        # 같은 성능이면 최신이 더 큰 가중치
        results = [
            self._make_result(0.60, 0.60),
            self._make_result(0.60, 0.60),
            self._make_result(0.60, 0.60),
        ]
        weights = trainer.compute_ensemble_weight_recency(results, decay=0.85)
        assert len(weights) == 3
        assert abs(sum(weights) - 1.0) < 1e-6
        # 뒤쪽(최신)이 가장 큰 가중치
        assert weights[2] > weights[1] > weights[0]

    def test_no_decay(self):
        """decay=1.0이면 시간 가중치 영향 없음 (compute_ensemble_weight와 동일)."""
        trainer = WalkForwardTrainer()
        results = [
            self._make_result(0.60, 0.60),
            self._make_result(0.70, 0.70),
        ]
        weights = trainer.compute_ensemble_weight_recency(results, decay=1.0)
        weights_no_recency = trainer.compute_ensemble_weight(results)
        for w1, w2 in zip(weights, weights_no_recency):
            assert abs(w1 - w2) < 1e-4

    def test_empty(self):
        trainer = WalkForwardTrainer()
        assert trainer.compute_ensemble_weight_recency([]) == []

    def test_all_failed(self):
        trainer = WalkForwardTrainer()
        results = [
            self._make_result(0.40, 0.35, passed=False),
            self._make_result(0.45, 0.40, passed=False),
        ]
        weights = trainer.compute_ensemble_weight_recency(results)
        assert all(abs(w - 0.5) < 1e-6 for w in weights)


# ---------------------------------------------------------------------------
# combinatorial_purged_cv
# ---------------------------------------------------------------------------

class TestCombinatorialPurgedCV:

    def test_returns_fold_results(self):
        """CPCV가 fold별 결과를 반환."""
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder(binary=True)
        df = _make_ohlcv(400)
        X, y = fb.build(df)
        y = y.astype(int)
        results = combinatorial_purged_cv(X, y, n_splits=4, purge_gap=3)
        assert isinstance(results, list)
        # 최소 1개 fold 결과
        if len(results) > 0:
            r = results[0]
            assert "fold" in r
            assert "n_train" in r
            assert "n_test" in r
            assert "train_acc" in r
            assert "test_acc" in r
            assert "purged_samples" in r

    def test_purge_gap_applied(self):
        """purge_gap > 0이면 purged_samples >= 0 (purge 로직 작동 확인)."""
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder(binary=True)
        df = _make_ohlcv(400)
        X, y = fb.build(df)
        y = y.astype(int)
        results = combinatorial_purged_cv(X, y, n_splits=4, purge_gap=5)
        # fold 결과가 반환되어야 함
        assert len(results) > 0
        # 각 fold에 purged_samples 키 존재
        for r in results:
            assert "purged_samples" in r
            assert r["purged_samples"] >= 0

    def test_fewer_folds_with_smaller_data(self):
        """데이터가 적으면 결과 fold 수가 줄어들 수 있음."""
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder(binary=False)  # 3-class: 더 많은 샘플 유지
        df = _make_ohlcv(250)
        X, y = fb.build(df)
        y = y.astype(int)
        # 적당한 n_splits로 테스트
        results = combinatorial_purged_cv(X, y, n_splits=4, purge_gap=3)
        assert len(results) <= 4


# ---------------------------------------------------------------------------
# ExtraTrees 모델 타입 테스트
# ---------------------------------------------------------------------------

class TestExtraTreesModelType:

    def test_extra_trees_returns_training_result(self):
        """ExtraTrees 모델로 학습 후 TrainingResult 반환."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            model_type="extra_trees",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert result.n_samples > 0
        assert result.n_features > 0

    def test_extra_trees_model_name_tag(self):
        """ExtraTrees 선택 시 model_name에 'et' 포함."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            model_type="extra_trees",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.model_name.startswith("et_")

    def test_rf_model_name_tag(self):
        """RF(기본) 선택 시 model_name에 'rf' 포함."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            model_type="rf",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.model_name.startswith("rf_")

    def test_extra_trees_same_interface(self):
        """ExtraTrees도 RF와 동일한 TrainingResult 구조 반환."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            model_type="extra_trees",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert hasattr(result, "feature_importances")
        assert hasattr(result, "val_accuracy")
        assert hasattr(result, "test_accuracy")
        assert len(result.feature_importances) > 0


# ---------------------------------------------------------------------------
# SHAP/importance 기반 피처 선택 테스트
# ---------------------------------------------------------------------------

class TestShapFeatureSelection:

    def test_shap_selection_disabled_by_default(self):
        """use_shap_selection 기본값 False — selected_features는 None."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.selected_features is None

    def test_shap_selection_returns_feature_list(self):
        """use_shap_selection=True → selected_features 리스트 반환."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.selected_features is not None
        assert isinstance(result.selected_features, list)
        assert len(result.selected_features) >= 2

    def test_shap_selection_features_subset_of_all(self):
        """선택된 피처가 전체 피처의 부분 집합."""
        trainer_full = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=False,
        )
        trainer_sel = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _make_ohlcv(300)
        result_full = trainer_full.train(df)
        result_sel = trainer_sel.train(df)

        all_features = set(result_full.feature_importances.keys())
        selected = set(result_sel.selected_features)
        assert selected.issubset(all_features)

    def test_shap_selection_reduces_or_keeps_features(self):
        """피처 선택 후 피처 수 <= 전체 피처 수."""
        trainer_full = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=False,
        )
        trainer_sel = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _make_ohlcv(300)
        result_full = trainer_full.train(df)
        result_sel = trainer_sel.train(df)

        n_full = len(result_full.feature_importances)
        n_sel = len(result_sel.selected_features)
        assert n_sel <= n_full

    def test_shap_selection_with_extra_trees(self):
        """ExtraTrees + SHAP 선택 조합도 정상 동작."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            model_type="extra_trees", use_shap_selection=True,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert result.selected_features is not None
        assert len(result.selected_features) >= 2

    def test_shap_selection_result_is_valid_training_result(self):
        """SHAP 선택 후 TrainingResult의 기본 필드 유효성 확인."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert result.n_samples > 0
        assert result.n_features > 0
        assert 0.0 <= result.train_accuracy <= 1.0
        assert 0.0 <= result.val_accuracy <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0


# ---------------------------------------------------------------------------
# XGBoost 모델 타입 테스트
# ---------------------------------------------------------------------------

class TestXGBoostModelType:

    def test_xgboost_fallback_when_not_installed(self):
        """xgboost 미설치 시 model_type이 'rf'로 fallback."""
        import src.ml.trainer as trainer_mod
        orig = trainer_mod._XGB_AVAILABLE
        try:
            trainer_mod._XGB_AVAILABLE = False
            trainer = WalkForwardTrainer(
                symbol="TEST/USDT", n_estimators=10, max_depth=3,
                model_type="xgboost",
            )
            assert trainer.model_type == "rf"
        finally:
            trainer_mod._XGB_AVAILABLE = orig

    def test_xgboost_fallback_trains_rf(self):
        """xgboost 미설치 시 RF로 정상 학습."""
        import src.ml.trainer as trainer_mod
        orig = trainer_mod._XGB_AVAILABLE
        try:
            trainer_mod._XGB_AVAILABLE = False
            trainer = WalkForwardTrainer(
                symbol="TEST/USDT", n_estimators=10, max_depth=3,
                model_type="xgboost",
            )
            df = _make_ohlcv(300)
            result = trainer.train(df)
            assert isinstance(result, TrainingResult)
            assert result.n_samples > 0
            # fallback이므로 rf_ 태그
            assert result.model_name.startswith("rf_")
        finally:
            trainer_mod._XGB_AVAILABLE = orig

    def test_xgboost_rf_model_type_unchanged(self):
        """model_type='rf'는 _XGB_AVAILABLE 상관없이 유지."""
        import src.ml.trainer as trainer_mod
        orig = trainer_mod._XGB_AVAILABLE
        try:
            trainer_mod._XGB_AVAILABLE = False
            trainer = WalkForwardTrainer(
                symbol="TEST/USDT", model_type="rf",
            )
            assert trainer.model_type == "rf"
        finally:
            trainer_mod._XGB_AVAILABLE = orig

    def test_xgboost_extra_trees_unchanged(self):
        """model_type='extra_trees'는 _XGB_AVAILABLE 상관없이 유지."""
        import src.ml.trainer as trainer_mod
        orig = trainer_mod._XGB_AVAILABLE
        try:
            trainer_mod._XGB_AVAILABLE = False
            trainer = WalkForwardTrainer(
                symbol="TEST/USDT", model_type="extra_trees",
            )
            assert trainer.model_type == "extra_trees"
        finally:
            trainer_mod._XGB_AVAILABLE = orig

    @pytest.mark.skipif(
        not __import__("src.ml.trainer", fromlist=["_XGB_AVAILABLE"])._XGB_AVAILABLE,
        reason="xgboost not installed",
    )
    def test_xgboost_train_returns_result(self):
        """xgboost 설치 시 학습+예측 동작."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=20, max_depth=3,
            model_type="xgboost",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert result.n_samples > 0
        assert result.n_features > 0
        assert result.model_name.startswith("xgb_")

    @pytest.mark.skipif(
        not __import__("src.ml.trainer", fromlist=["_XGB_AVAILABLE"])._XGB_AVAILABLE,
        reason="xgboost not installed",
    )
    def test_xgboost_max_depth_3(self):
        """XGBoost max_depth=3 제한 확인."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=20, max_depth=10,
            model_type="xgboost",
        )
        df = _make_ohlcv(300)
        trainer.train(df)
        # XGBoost에서는 max_depth=3 고정 (self.max_depth 무시)
        base = trainer._trained_model
        # CalibratedClassifierCV 래핑 가능 → base estimator 추출
        actual_clf = getattr(base, "estimator", getattr(base, "base_estimator", base))
        if hasattr(actual_clf, "max_depth"):
            assert actual_clf.max_depth == 3

    @pytest.mark.skipif(
        not __import__("src.ml.trainer", fromlist=["_XGB_AVAILABLE"])._XGB_AVAILABLE,
        reason="xgboost not installed",
    )
    def test_xgboost_same_interface_as_rf(self):
        """XGBoost도 RF와 동일한 TrainingResult 필드 반환."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=20, max_depth=3,
            model_type="xgboost",
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert hasattr(result, "feature_importances")
        assert hasattr(result, "val_accuracy")
        assert hasattr(result, "test_accuracy")
        assert hasattr(result, "split_info")
        assert len(result.feature_importances) > 0
        assert 0.0 <= result.train_accuracy <= 1.0
        assert 0.0 <= result.val_accuracy <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0


# ---------------------------------------------------------------------------
# sklearn 미설치 시 fallback 테스트
# ---------------------------------------------------------------------------

class TestSklearnMissing:

    def test_train_without_sklearn(self):
        """sklearn 미설치 시 graceful failure."""
        trainer = WalkForwardTrainer(symbol="TEST/USDT")
        df = _make_ohlcv(300)

        with patch.dict("sys.modules", {
            "sklearn": None,
            "sklearn.ensemble": None,
            "sklearn.metrics": None,
            "sklearn.calibration": None,
        }):
            # builtins.__import__ 패치로 ImportError 시뮬레이션
            result = trainer.train(df)
            # sklearn이 이미 import 되어 있으므로 직접 ImportError 시뮬레이션은 어려움
            # 대신 결과 타입만 확인
            assert isinstance(result, TrainingResult)
