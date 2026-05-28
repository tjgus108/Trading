"""
레짐별 피처 중요도 + Feature Drift 통합 테스트.

작업 1: RegimeAwareFeatureBuilder.get_feature_importance_by_regime()
작업 2: DualGateADWINMonitor.check_feature_drift()
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.features import RegimeAwareFeatureBuilder
from src.ml.drift_detector import DualGateADWINMonitor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """합성 OHLCV 데이터 생성."""
    rng = np.random.default_rng(seed)
    closes = 100.0 + np.cumsum(rng.standard_normal(n) * 0.5)
    closes = np.abs(closes) + 50.0
    return pd.DataFrame({
        "open": closes * (1 + rng.standard_normal(n) * 0.001),
        "high": closes * (1 + np.abs(rng.standard_normal(n)) * 0.005),
        "low": closes * (1 - np.abs(rng.standard_normal(n)) * 0.005),
        "close": closes,
        "volume": rng.uniform(100, 2000, n),
    })


def _make_regime_labels(index, regimes=("bull", "bear", "ranging"), seed=42):
    """인덱스에 맞는 랜덤 레짐 레이블 생성."""
    rng = np.random.default_rng(seed)
    labels = rng.choice(list(regimes), size=len(index))
    return pd.Series(labels, index=index, name="regime")


# ===========================================================================
# 작업 1: get_feature_importance_by_regime 테스트 (6개)
# ===========================================================================


class TestGetFeatureImportanceByRegime:
    """RegimeAwareFeatureBuilder.get_feature_importance_by_regime() 검증."""

    def test_basic_returns_dict_per_regime(self):
        """기본: 여러 레짐이 있는 데이터 → 레짐별 중요도 dict 반환."""
        df = _make_ohlcv(300)
        builder = RegimeAwareFeatureBuilder()
        X, y = builder.build(df)
        regime_labels = _make_regime_labels(X.index, regimes=("bull", "bear"))

        result = builder.get_feature_importance_by_regime(X, y, regime_labels)

        assert isinstance(result, dict)
        assert len(result) > 0
        for regime, imp_dict in result.items():
            assert isinstance(imp_dict, dict)
            assert len(imp_dict) > 0
            # 중요도 합계 ≈ 1.0
            total = sum(imp_dict.values())
            assert abs(total - 1.0) < 0.01, f"Regime {regime}: importance sum={total}"

    def test_skips_regime_with_few_samples(self):
        """min_samples 미달 레짐은 결과에서 제외."""
        df = _make_ohlcv(200)
        builder = RegimeAwareFeatureBuilder()
        X, y = builder.build(df)

        # 대부분 bull, 극소수 crisis
        labels = pd.Series("bull", index=X.index, name="regime")
        labels.iloc[:5] = "crisis"  # 5개만 crisis

        result = builder.get_feature_importance_by_regime(
            X, y, labels, min_samples=30
        )

        assert "bull" in result
        assert "crisis" not in result, "crisis(5 samples) should be skipped"

    def test_empty_inputs_return_empty(self):
        """빈 X, y → 빈 dict 반환."""
        builder = RegimeAwareFeatureBuilder()
        result = builder.get_feature_importance_by_regime(
            pd.DataFrame(), pd.Series(dtype=float), pd.Series(dtype=str)
        )
        assert result == {}

    def test_single_regime(self):
        """단일 레짐만 있는 경우 → 해당 레짐의 중요도만 반환."""
        df = _make_ohlcv(200)
        builder = RegimeAwareFeatureBuilder()
        X, y = builder.build(df)
        labels = pd.Series("bull", index=X.index, name="regime")

        result = builder.get_feature_importance_by_regime(X, y, labels)

        assert len(result) == 1
        assert "bull" in result
        assert len(result["bull"]) == len(X.columns)

    def test_feature_names_match_columns(self):
        """반환된 피처명이 X의 컬럼과 일치."""
        df = _make_ohlcv(300)
        builder = RegimeAwareFeatureBuilder()
        X, y = builder.build(df)
        labels = _make_regime_labels(X.index, regimes=("bull", "bear"))

        result = builder.get_feature_importance_by_regime(X, y, labels)

        for regime, imp_dict in result.items():
            assert set(imp_dict.keys()) == set(X.columns), \
                f"Regime {regime}: feature names mismatch"

    def test_skips_single_class_regime(self):
        """레짐 내 y가 단일 클래스면 스킵."""
        df = _make_ohlcv(200)
        builder = RegimeAwareFeatureBuilder()
        X, y = builder.build(df)

        # all_same 레짐: y를 모두 1로 설정
        labels = pd.Series("bull", index=X.index, name="regime")
        labels.iloc[:50] = "constant_class"
        y_modified = y.copy()
        y_modified.iloc[:50] = 1  # 단일 클래스

        result = builder.get_feature_importance_by_regime(
            X, y_modified, labels, min_samples=10
        )

        # constant_class 레짐은 단일 클래스이므로 스킵
        assert "constant_class" not in result


# ===========================================================================
# 작업 2: check_feature_drift 테스트 (6개)
# ===========================================================================


class TestCheckFeatureDrift:
    """DualGateADWINMonitor.check_feature_drift() 검증."""

    def test_no_drift_same_stats(self):
        """동일 통계 → drift 없음."""
        monitor = DualGateADWINMonitor()
        baseline = {
            "return_1": {"mean": 0.001, "std": 0.02},
            "atr_pct": {"mean": 0.015, "std": 0.005},
        }
        current = {
            "return_1": {"mean": 0.001, "std": 0.02},
            "atr_pct": {"mean": 0.015, "std": 0.005},
        }

        result = monitor.check_feature_drift(baseline, current)

        assert result["is_drifting"] is False
        assert result["drifted_features"] == []
        assert len(result["drift_scores"]) == 2
        assert all(v == 0.0 for v in result["drift_scores"].values())

    def test_drift_detected_large_shift(self):
        """mean이 크게 변화 → drift 감지."""
        monitor = DualGateADWINMonitor()
        baseline = {
            "return_1": {"mean": 0.001, "std": 0.02},
            "atr_pct": {"mean": 0.015, "std": 0.005},
        }
        current = {
            "return_1": {"mean": 0.001, "std": 0.02},  # 변화 없음
            "atr_pct": {"mean": 0.050, "std": 0.005},  # (0.05-0.015)/0.005=7.0 > 2.0
        }

        result = monitor.check_feature_drift(baseline, current)

        assert result["is_drifting"] is True
        assert "atr_pct" in result["drifted_features"]
        assert "return_1" not in result["drifted_features"]
        assert result["drift_scores"]["atr_pct"] == 7.0

    def test_custom_threshold(self):
        """threshold 변경 → 민감도 조절."""
        monitor = DualGateADWINMonitor()
        baseline = {"f1": {"mean": 1.0, "std": 0.5}}
        current = {"f1": {"mean": 2.0, "std": 0.5}}  # score=2.0

        # threshold=2.0 → not drifted (score > threshold 필요, 2.0 == 2.0는 안됨)
        result_default = monitor.check_feature_drift(baseline, current, threshold=2.0)
        assert result_default["is_drifting"] is False

        # threshold=1.5 → drifted
        result_sensitive = monitor.check_feature_drift(baseline, current, threshold=1.5)
        assert result_sensitive["is_drifting"] is True

    def test_zero_std_constant_feature(self):
        """baseline std=0 (상수 피처) → mean 변화 시 drift."""
        monitor = DualGateADWINMonitor()
        baseline = {"const_feat": {"mean": 5.0, "std": 0.0}}
        current_same = {"const_feat": {"mean": 5.0, "std": 0.0}}
        current_diff = {"const_feat": {"mean": 5.1, "std": 0.0}}

        # 동일 → drift 없음
        r1 = monitor.check_feature_drift(baseline, current_same)
        assert r1["is_drifting"] is False

        # 다름 → drift 감지
        r2 = monitor.check_feature_drift(baseline, current_diff)
        assert r2["is_drifting"] is True
        assert "const_feat" in r2["drifted_features"]

    def test_missing_feature_in_current(self):
        """current에 없는 피처는 무시."""
        monitor = DualGateADWINMonitor()
        baseline = {
            "f1": {"mean": 1.0, "std": 0.5},
            "f2": {"mean": 2.0, "std": 0.3},
        }
        current = {
            "f1": {"mean": 1.0, "std": 0.5},
            # f2 누락
        }

        result = monitor.check_feature_drift(baseline, current)

        assert result["is_drifting"] is False
        assert "f1" in result["drift_scores"]
        assert "f2" not in result["drift_scores"]

    def test_result_structure(self):
        """반환 구조가 정확한지 검증."""
        monitor = DualGateADWINMonitor()
        baseline = {"f1": {"mean": 0.0, "std": 1.0}}
        current = {"f1": {"mean": 3.0, "std": 1.0}}

        result = monitor.check_feature_drift(baseline, current)

        assert "drifted_features" in result
        assert "drift_scores" in result
        assert "is_drifting" in result
        assert isinstance(result["drifted_features"], list)
        assert isinstance(result["drift_scores"], dict)
        assert isinstance(result["is_drifting"], bool)
