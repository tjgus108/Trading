"""
Tests for PFI-based feature selection in WalkForwardTrainer.train().
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.trainer import WalkForwardTrainer


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _make_df(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = 50000 + np.cumsum(rng.standard_normal(n) * 300)
    close = np.abs(close)
    high = close + np.abs(rng.standard_normal(n) * 100)
    low = close - np.abs(rng.standard_normal(n) * 100)
    low = np.maximum(low, close * 0.9)
    volume = 10.0 + np.abs(rng.standard_normal(n) * 2)
    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    return df


# ─────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────

class TestFeatureSelectionDefault:
    """feature_selection=False(기본) 시 기존 동작 유지."""

    def test_feature_selection_false_no_selected_features(self):
        """feature_selection=False이면 selected_features는 None."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=False)
        # use_shap_selection=False이므로 selected_features=None
        assert result.selected_features is None

    def test_feature_selection_false_uses_all_features(self):
        """feature_selection=False이면 n_features가 전체 피처 수."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=False)
        # 기본 피처 수 (14개, optional 피처 없음)
        assert result.n_features >= 14

    def test_train_returns_training_result(self):
        """train()은 항상 TrainingResult를 반환."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df)
        assert hasattr(result, "passed")
        assert hasattr(result, "n_features")
        assert hasattr(result, "selected_features")


class TestFeatureSelectionEnabled:
    """feature_selection=True 시 PFI 피처 선택 동작."""

    def test_feature_selection_reduces_features(self):
        """feature_selection=True이면 n_features <= 원래 피처 수."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result_base = trainer.train(df, feature_selection=False)
        trainer2 = WalkForwardTrainer(symbol="BTC/USDT")
        result_sel = trainer2.train(df, feature_selection=True, top_k=8)
        assert result_sel.n_features <= result_base.n_features

    def test_feature_selection_top_k_respected(self):
        """feature_selection=True + top_k=6이면 n_features <= 6."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=True, top_k=6)
        assert result.n_features <= 6

    def test_feature_selection_sets_selected_features(self):
        """feature_selection=True이면 selected_features 목록이 반환됨."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=True, top_k=8)
        assert result.selected_features is not None
        assert len(result.selected_features) >= 2

    def test_feature_selection_top_k_8_default(self):
        """top_k 기본값 8이면 selected_features 수 <= 8."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=True)
        assert result.selected_features is not None
        assert len(result.selected_features) <= 8

    def test_feature_selection_result_valid(self):
        """feature_selection=True 결과도 TrainingResult 필드가 모두 유효."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        result = trainer.train(df, feature_selection=True, top_k=8)
        assert 0.0 <= result.train_accuracy <= 1.0
        assert 0.0 <= result.val_accuracy <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0
        assert result.n_samples > 0
        assert result.n_features > 0

    def test_feature_selection_trained_model_uses_reduced_features(self):
        """재학습 후 trainer._feature_names가 top_k 이하."""
        df = _make_df(300)
        trainer = WalkForwardTrainer(symbol="BTC/USDT")
        trainer.train(df, feature_selection=True, top_k=6)
        assert len(trainer._feature_names) <= 6


class TestSelectFeaturesPfi:
    """select_features_pfi() 메서드 단위 테스트."""

    def _fit_rf(self, X, y):
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=20, max_depth=3, random_state=42)
        clf.fit(X, y)
        return clf

    def test_returns_list_of_strings(self):
        """반환값은 문자열 리스트."""
        df = _make_df(200)
        trainer = WalkForwardTrainer()
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, y = fb.build(df)
        y = y.astype(int)
        clf = self._fit_rf(X, y)
        result = trainer.select_features_pfi(clf, X, y, top_k=6)
        assert isinstance(result, list)
        assert all(isinstance(f, str) for f in result)

    def test_returns_top_k_features(self):
        """top_k개 이하 피처 반환."""
        df = _make_df(200)
        trainer = WalkForwardTrainer()
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, y = fb.build(df)
        y = y.astype(int)
        clf = self._fit_rf(X, y)
        result = trainer.select_features_pfi(clf, X, y, top_k=5)
        assert len(result) <= 5

    def test_minimum_two_features_guaranteed(self):
        """top_k=1이어도 최소 2개 반환."""
        df = _make_df(200)
        trainer = WalkForwardTrainer()
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, y = fb.build(df)
        y = y.astype(int)
        clf = self._fit_rf(X, y)
        result = trainer.select_features_pfi(clf, X, y, top_k=1)
        assert len(result) >= 2

    def test_selected_features_are_subset_of_columns(self):
        """선택된 피처는 원래 컬럼의 부분 집합."""
        df = _make_df(200)
        trainer = WalkForwardTrainer()
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, y = fb.build(df)
        y = y.astype(int)
        clf = self._fit_rf(X, y)
        result = trainer.select_features_pfi(clf, X, y, top_k=8)
        assert set(result).issubset(set(X.columns))

    def test_top_k_larger_than_features_returns_all(self):
        """top_k가 전체 피처 수보다 크면 전체 반환."""
        df = _make_df(200)
        trainer = WalkForwardTrainer()
        from src.ml.features import FeatureBuilder
        fb = FeatureBuilder()
        X, y = fb.build(df)
        y = y.astype(int)
        clf = self._fit_rf(X, y)
        result = trainer.select_features_pfi(clf, X, y, top_k=999)
        assert len(result) == len(X.columns)
