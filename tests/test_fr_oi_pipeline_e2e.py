"""
End-to-end tests: FR/OI 피처 파이프라인 검증.

데이터(feed) → FeatureBuilder → Trainer 전체 흐름.
- FR/OI 피처가 학습 데이터에 포함되는지 확인
- 컬럼 유/무에 따른 피처 수 차이
- NaN/Inf graceful handling
- 빈 데이터 fallback
- SHAP 선택 후 FR/OI 피처 유지 확인
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.features import FeatureBuilder
from src.ml.trainer import WalkForwardTrainer, TrainingResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """학습 파이프라인 테스트용 OHLCV."""
    rng = np.random.RandomState(seed)
    close = 50000.0 + np.cumsum(rng.randn(n) * 100)
    close = np.maximum(close, 1000.0)
    high = close + rng.uniform(10, 200, n)
    low = close - rng.uniform(10, 200, n)
    volume = rng.uniform(100, 2000, n)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame({
        "open": close + rng.randn(n) * 30,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }, index=idx)


def _add_fr_oi(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """funding_rate + open_interest 컬럼 추가."""
    rng = np.random.RandomState(seed)
    df = df.copy()
    df["funding_rate"] = rng.uniform(-0.001, 0.001, len(df))
    df["open_interest"] = rng.uniform(5000, 50000, len(df))
    return df


# ---------------------------------------------------------------------------
# 1. End-to-end: FeatureBuilder 피처 수 차이 검증
# ---------------------------------------------------------------------------

class TestFeatureCountDiff:
    """FR/OI 컬럼 유/무에 따른 피처 수 차이 확인."""

    def test_no_fr_oi_base_14_features(self):
        """FR/OI 없이 base 14 피처만 생성."""
        fb = FeatureBuilder()
        df = _make_ohlcv(100)
        X, y = fb.build(df)
        assert len(X.columns) == 14
        assert "delta_fr" not in X.columns
        assert "fr_oi_interaction" not in X.columns

    def test_fr_only_15_features(self):
        """funding_rate만 있으면 base 14 + delta_fr = 15."""
        fb = FeatureBuilder()
        df = _make_ohlcv(100)
        df["funding_rate"] = np.random.uniform(-0.001, 0.001, len(df))
        X, y = fb.build(df)
        assert len(X.columns) == 15
        assert "delta_fr" in X.columns
        assert "fr_oi_interaction" not in X.columns

    def test_fr_and_oi_16_features(self):
        """funding_rate + open_interest 둘 다 있으면 base 14 + 2 = 16."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        X, y = fb.build(df)
        assert len(X.columns) == 16
        assert "delta_fr" in X.columns
        assert "fr_oi_interaction" in X.columns

    def test_btc_close_plus_fr_oi_17_features(self):
        """btc_close + funding_rate + open_interest → 17 피처."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df["btc_close"] = df["close"] * 1.1  # dummy BTC close
        X, y = fb.build(df)
        assert len(X.columns) == 17
        assert "btc_close_lag1" in X.columns
        assert "delta_fr" in X.columns
        assert "fr_oi_interaction" in X.columns


# ---------------------------------------------------------------------------
# 2. End-to-end: Trainer에 FR/OI 피처 전달 검증
# ---------------------------------------------------------------------------

class TestTrainerWithFrOi:
    """WalkForwardTrainer가 FR/OI 피처를 정상 학습하는지 검증."""

    def test_train_with_fr_oi_features(self):
        """FR/OI 포함 데이터로 학습 시 피처 목록에 delta_fr, fr_oi 포함."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        df = _add_fr_oi(_make_ohlcv(300))
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert "delta_fr" in result.feature_importances
        assert "fr_oi_interaction" in result.feature_importances
        assert result.n_features == 16

    def test_train_without_fr_oi_features(self):
        """FR/OI 없는 데이터로 학습 시 base 14 피처만."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        df = _make_ohlcv(300)
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert "delta_fr" not in result.feature_importances
        assert "fr_oi_interaction" not in result.feature_importances
        assert result.n_features == 14

    def test_feature_count_diff_trainer_level(self):
        """Trainer 레벨에서 FR/OI 유무에 따른 n_features 차이 = 2."""
        t_base = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        t_froi = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        df_base = _make_ohlcv(300)
        df_froi = _add_fr_oi(_make_ohlcv(300))

        r_base = t_base.train(df_base)
        r_froi = t_froi.train(df_froi)

        assert r_froi.n_features - r_base.n_features == 2

    def test_fr_oi_features_in_importance_ranking(self):
        """FR/OI 피처가 중요도 순위에 포함되는지 확인."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
        )
        df = _add_fr_oi(_make_ohlcv(300))
        trainer.train(df)
        importances = trainer.get_feature_importances()
        feature_names = [name for name, _ in importances]
        assert "delta_fr" in feature_names
        assert "fr_oi_interaction" in feature_names


# ---------------------------------------------------------------------------
# 3. NaN/Inf graceful handling
# ---------------------------------------------------------------------------

class TestFrOiDataQuality:
    """FR/OI 데이터에 NaN/Inf가 있을 때 안전한 처리 확인."""

    def test_nan_in_funding_rate(self):
        """funding_rate에 NaN 포함 → build() 후 NaN 행 제거."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        # 일부 NaN 삽입
        df.loc[df.index[10], "funding_rate"] = np.nan
        df.loc[df.index[20], "funding_rate"] = np.nan
        X, y = fb.build(df)
        assert not X.isna().any().any(), "NaN이 남아있으면 안 됨"
        assert not np.isinf(X.values).any(), "inf가 남아있으면 안 됨"

    def test_nan_in_open_interest(self):
        """open_interest에 NaN → fr_oi_interaction도 NaN → dropna 처리."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df.loc[df.index[15], "open_interest"] = np.nan
        X, y = fb.build(df)
        assert not X.isna().any().any()

    def test_inf_in_funding_rate(self):
        """funding_rate에 Inf → inf→NaN 변환 후 dropna."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df.loc[df.index[10], "funding_rate"] = np.inf
        df.loc[df.index[11], "funding_rate"] = -np.inf
        X, y = fb.build(df)
        assert not np.isinf(X.values).any(), "inf가 NaN으로 변환되어야 함"
        assert not X.isna().any().any()

    def test_zero_open_interest(self):
        """OI=0 → oi_norm 분모에 1e-9 보호 → inf 미발생."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df["open_interest"] = 0.0  # 모든 OI=0
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()

    def test_all_nan_funding_rate(self):
        """funding_rate 전부 NaN → delta_fr도 전부 NaN → dropna로 행 감소."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df["funding_rate"] = np.nan
        X, y = fb.build(df)
        # delta_fr 컬럼은 생성되지만 모든 행이 NaN → dropna로 제거
        # build()가 빈 X를 반환하거나 줄어든 행 반환
        assert not X.isna().any().any()
        # 대부분 행이 제거될 수 있음
        assert len(X) == 0 or "delta_fr" in X.columns

    def test_mixed_nan_inf_graceful(self):
        """NaN + Inf 혼합 → build()가 안전하게 처리."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df.loc[df.index[5], "funding_rate"] = np.nan
        df.loc[df.index[10], "funding_rate"] = np.inf
        df.loc[df.index[15], "open_interest"] = np.nan
        df.loc[df.index[20], "open_interest"] = -np.inf
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()
        assert not X.isna().any().any()


# ---------------------------------------------------------------------------
# 4. 빈 데이터 / 엣지케이스 fallback
# ---------------------------------------------------------------------------

class TestFrOiEdgeCases:
    """빈 데이터 및 경계값에서의 동작 확인."""

    def test_single_value_funding_rate(self):
        """funding_rate가 단일 값 → delta_fr[0]=NaN, 나머지=0."""
        fb = FeatureBuilder()
        df = _make_ohlcv(100)
        df["funding_rate"] = 0.0001  # 상수
        feat = fb._compute_features(df)
        # diff of constant = 0 (except first = NaN)
        assert np.isnan(feat["delta_fr"].iloc[0])
        assert feat["delta_fr"].iloc[5] == 0.0

    def test_negative_open_interest(self):
        """음수 OI (이론적으로 발생 불가하지만 방어)."""
        fb = FeatureBuilder()
        df = _add_fr_oi(_make_ohlcv(100))
        df["open_interest"] = -100.0  # 음수
        X, y = fb.build(df)
        # inf/NaN 없이 처리되어야 함
        assert not np.isinf(X.values).any()
        assert not X.isna().any().any()

    def test_very_large_funding_rate(self):
        """극단적으로 큰 FR → overflow 없이 처리."""
        fb = FeatureBuilder()
        df = _make_ohlcv(100)
        df["funding_rate"] = 1e10
        df["open_interest"] = 1e15
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()
        assert not X.isna().any().any()

    def test_very_small_funding_rate(self):
        """극소 FR (1e-15) → underflow 없이 처리."""
        fb = FeatureBuilder()
        df = _make_ohlcv(100)
        df["funding_rate"] = 1e-15
        df["open_interest"] = 1.0
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()
        assert not X.isna().any().any()


# ---------------------------------------------------------------------------
# 5. SHAP 선택 후 FR/OI 피처 유지 검증
# ---------------------------------------------------------------------------

class TestShapSelectionWithFrOi:
    """SHAP/importance 피처 선택이 FR/OI 피처에 미치는 영향."""

    def test_shap_selection_with_fr_oi_data(self):
        """FR/OI 포함 데이터 + SHAP 선택 → 정상 학습."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _add_fr_oi(_make_ohlcv(300))
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        assert result.selected_features is not None
        assert len(result.selected_features) >= 2

    def test_shap_selected_features_are_subset(self):
        """SHAP 선택된 피처가 전체(FR/OI 포함) 피처의 부분 집합."""
        trainer_full = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=False,
        )
        trainer_sel = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _add_fr_oi(_make_ohlcv(300))
        r_full = trainer_full.train(df)
        r_sel = trainer_sel.train(df)
        all_feats = set(r_full.feature_importances.keys())
        selected = set(r_sel.selected_features)
        assert selected.issubset(all_feats)

    def test_shap_selection_result_valid(self):
        """SHAP 선택 + FR/OI → TrainingResult 필드 유효."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            use_shap_selection=True,
        )
        df = _add_fr_oi(_make_ohlcv(300))
        result = trainer.train(df)
        assert result.n_samples > 0
        assert result.n_features > 0
        assert result.n_features <= 16  # base 14 + delta_fr + fr_oi_interaction
        assert 0.0 <= result.train_accuracy <= 1.0
        assert 0.0 <= result.val_accuracy <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0


# ---------------------------------------------------------------------------
# 6. DataFeed.compute_fr_oi_features → FeatureBuilder 일관성
# ---------------------------------------------------------------------------

class TestFeedToFeatureBuilderConsistency:
    """DataFeed.compute_fr_oi_features와 FeatureBuilder 내부 계산 일관성."""

    def test_delta_fr_consistency(self):
        """DataFeed.compute_fr_oi_features의 delta_fr와 FeatureBuilder의 delta_fr 일치."""
        from src.data.feed import DataFeed

        n = 100
        idx = pd.date_range("2024-01-01", periods=n, freq="1h")
        rng = np.random.RandomState(42)
        fr = pd.Series(rng.uniform(-0.001, 0.001, n), index=idx)
        oi = pd.Series(rng.uniform(5000, 50000, n), index=idx)

        # DataFeed 방식
        feed_result = DataFeed.compute_fr_oi_features(fr, oi)

        # FeatureBuilder 방식: DataFrame에 fr/oi 넣고 피처 추출
        close = 50000 + np.cumsum(rng.randn(n) * 100)
        close = np.maximum(close, 1000.0)
        df = pd.DataFrame({
            "open": close, "high": close * 1.005, "low": close * 0.995,
            "close": close, "volume": rng.uniform(100, 1000, n),
            "funding_rate": fr.values, "open_interest": oi.values,
        }, index=idx)

        fb = FeatureBuilder()
        feat = fb._compute_features(df)

        # delta_fr 일치
        pd.testing.assert_series_equal(
            feed_result["delta_fr"].dropna(),
            feat["delta_fr"].dropna(),
            check_names=False,
        )

    def test_fr_oi_interaction_consistency(self):
        """fr_oi_interaction 계산 방식 일관성."""
        from src.data.feed import DataFeed

        n = 50
        idx = pd.date_range("2024-01-01", periods=n, freq="1h")
        rng = np.random.RandomState(99)
        fr_vals = rng.uniform(-0.001, 0.001, n)
        oi_vals = rng.uniform(5000, 50000, n)

        fr = pd.Series(fr_vals, index=idx)
        oi = pd.Series(oi_vals, index=idx)

        feed_result = DataFeed.compute_fr_oi_features(fr, oi)

        close = 50000 + np.cumsum(rng.randn(n) * 100)
        close = np.maximum(close, 1000.0)
        df = pd.DataFrame({
            "open": close, "high": close * 1.005, "low": close * 0.995,
            "close": close, "volume": rng.uniform(100, 1000, n),
            "funding_rate": fr_vals, "open_interest": oi_vals,
        }, index=idx)

        fb = FeatureBuilder()
        feat = fb._compute_features(df)

        # fr_oi_interaction 일치
        pd.testing.assert_series_equal(
            feed_result["fr_oi_interaction"].dropna(),
            feat["fr_oi_interaction"].dropna(),
            check_names=False,
        )


# ---------------------------------------------------------------------------
# 7. Triple Barrier + FR/OI 조합
# ---------------------------------------------------------------------------

class TestTripleBarrierWithFrOi:
    """Triple Barrier 레이블링 + FR/OI 피처 조합."""

    def test_triple_barrier_with_fr_oi(self):
        """TB 모드에서도 FR/OI 피처 정상 포함."""
        fb = FeatureBuilder(binary=True, triple_barrier=True)
        df = _add_fr_oi(_make_ohlcv(200))
        X, y = fb.build(df)
        if len(X) > 0:
            assert "delta_fr" in X.columns
            assert "fr_oi_interaction" in X.columns
            assert not X.isna().any().any()

    def test_triple_barrier_trainer_with_fr_oi(self):
        """TB + FR/OI로 Trainer 학습."""
        trainer = WalkForwardTrainer(
            symbol="TEST/USDT", n_estimators=10, max_depth=3,
            binary=True, triple_barrier=True,
        )
        df = _add_fr_oi(_make_ohlcv(400))
        result = trainer.train(df)
        assert isinstance(result, TrainingResult)
        # TB는 샘플 줄어들 수 있으므로 n_samples 체크만
        if result.n_samples >= 100:
            assert "delta_fr" in result.feature_importances
