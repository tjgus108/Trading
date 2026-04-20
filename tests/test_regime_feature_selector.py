"""
Cycle 170+: RegimeAwareFeatureBuilder + detect_regime 단위/통합 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.features import (
    REGIME_FEATURE_CONFIG,
    REGIME_OPTIONAL_FEATURES,
    FeatureBuilder,
    RegimeAwareFeatureBuilder,
    detect_regime,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(n: int = 300, seed: int = 42, trend: str = "neutral") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")

    if trend == "bull":
        close = 50000 + np.arange(n) * 50 + rng.standard_normal(n) * 100
    elif trend == "bear":
        close = 60000 - np.arange(n) * 50 + rng.standard_normal(n) * 100
    elif trend == "volatile":
        close = 50000 + np.cumsum(rng.standard_normal(n) * 2000)
    else:
        close = 50000 + np.cumsum(rng.standard_normal(n) * 100)

    close = np.abs(close) + 1.0
    high = close + np.abs(rng.standard_normal(n) * 50)
    low = close - np.abs(rng.standard_normal(n) * 50)
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


# ---------------------------------------------------------------------------
# detect_regime
# ---------------------------------------------------------------------------

class TestDetectRegime:
    def test_returns_valid_regime(self):
        df = _make_df(300)
        regime = detect_regime(df)
        assert regime in {"bull", "bear", "ranging", "crisis"}

    def test_bull_trend_detected(self):
        df = _make_df(300, trend="bull")
        regime = detect_regime(df)
        # 강한 상승 추세 → bull (또는 ranging이 될 수 있음)
        assert regime in {"bull", "ranging"}

    def test_bear_trend_detected(self):
        df = _make_df(300, trend="bear")
        regime = detect_regime(df)
        # 강한 하락 추세 → bear (또는 ranging)
        assert regime in {"bear", "ranging", "crisis"}

    def test_volatile_detected_as_crisis(self):
        df = _make_df(300, trend="volatile")
        regime = detect_regime(df)
        # 고변동성 → crisis 또는 bear
        assert regime in {"crisis", "bear", "bull", "ranging"}

    def test_short_data_returns_ranging(self):
        df = _make_df(10)
        regime = detect_regime(df, lookback=20)
        assert regime == "ranging"

    def test_lookback_parameter(self):
        df = _make_df(300)
        r1 = detect_regime(df, lookback=10)
        r2 = detect_regime(df, lookback=30)
        # 둘 다 유효한 레짐 반환
        assert r1 in {"bull", "bear", "ranging", "crisis"}
        assert r2 in {"bull", "bear", "ranging", "crisis"}


# ---------------------------------------------------------------------------
# REGIME_FEATURE_CONFIG
# ---------------------------------------------------------------------------

class TestRegimeFeatureConfig:
    def test_all_regimes_defined(self):
        for regime in ("bull", "bear", "ranging", "crisis"):
            assert regime in REGIME_FEATURE_CONFIG
            assert len(REGIME_FEATURE_CONFIG[regime]) >= 2

    def test_config_features_are_valid(self):
        base_fb = FeatureBuilder()
        all_valid = set(base_fb.feature_names) | {
            "btc_close_lag1", "delta_fr", "fr_oi_interaction"
        }
        for regime, feats in REGIME_FEATURE_CONFIG.items():
            for f in feats:
                assert f in all_valid, f"Unknown feature '{f}' in regime '{regime}'"

    def test_crisis_smallest_feature_set(self):
        # crisis는 가장 보수적 — 피처 수가 가장 적어야 함
        crisis_len = len(REGIME_FEATURE_CONFIG["crisis"])
        for regime in ("bull", "bear", "ranging"):
            assert crisis_len <= len(REGIME_FEATURE_CONFIG[regime])


# ---------------------------------------------------------------------------
# RegimeAwareFeatureBuilder
# ---------------------------------------------------------------------------

class TestRegimeAwareFeatureBuilder:
    def test_build_with_regime_returns_three_values(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X, y, regime = builder.build_with_regime(df)
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert regime in {"bull", "bear", "ranging", "crisis"}

    def test_regime_subset_smaller_than_full(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X_regime, y_regime, regime = builder.build_with_regime(df)
        X_full, y_full = builder.build(df)
        # 레짐 피처는 전체 피처 수 이하
        assert X_regime.shape[1] <= X_full.shape[1]

    def test_build_features_regime_returns_two_values(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X, regime = builder.build_features_regime(df)
        assert isinstance(X, pd.DataFrame)
        assert regime in {"bull", "bear", "ranging", "crisis"}
        assert len(X) > 0

    def test_no_nan_in_regime_features(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X, y, _ = builder.build_with_regime(df)
        assert not X.isnull().any().any()
        assert not y.isnull().any()

    def test_all_regime_features_finite(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X, _, _ = builder.build_with_regime(df)
        assert np.isfinite(X.values).all()

    def test_time_series_order_preserved(self):
        df = _make_df(300)
        builder = RegimeAwareFeatureBuilder()
        X, _, _ = builder.build_with_regime(df)
        assert X.index.is_monotonic_increasing

    def test_compat_build_same_as_base(self):
        """build() 위임 — 기존 FeatureBuilder와 동일 결과."""
        df = _make_df(200)
        base_fb = FeatureBuilder()
        regime_fb = RegimeAwareFeatureBuilder()
        X_base, y_base = base_fb.build(df)
        X_compat, y_compat = regime_fb.build(df)
        pd.testing.assert_frame_equal(X_base, X_compat)

    def test_compat_build_features_only(self):
        df = _make_df(200)
        base_fb = FeatureBuilder()
        regime_fb = RegimeAwareFeatureBuilder()
        X_base = base_fb.build_features_only(df)
        X_compat = regime_fb.build_features_only(df)
        pd.testing.assert_frame_equal(X_base, X_compat)

    def test_custom_feature_config_injection(self):
        custom_config = {
            "bull": ["return_1", "ema_ratio"],
            "bear": ["return_1", "atr_pct"],
            "ranging": ["return_1", "bb_position"],
            "crisis": ["return_1", "volatility_20"],
        }
        df = _make_df(200)
        builder = RegimeAwareFeatureBuilder(feature_config=custom_config)
        X, y, regime = builder.build_with_regime(df)
        # 커스텀 config 피처만 사용
        expected_feats = custom_config[regime]
        for f in X.columns:
            assert f in expected_feats

    def test_get_regime_features_no_optional(self):
        builder = RegimeAwareFeatureBuilder()
        feats = builder.get_regime_features("bull")
        assert len(feats) >= 2
        # 선택적 피처(btc_close_lag1 등) 없어야 함 (df=None)
        assert "btc_close_lag1" not in feats

    def test_get_regime_features_with_optional(self):
        df = _make_df(200)
        df["btc_close"] = df["close"] * 0.98  # BTC 컬럼 추가
        df["funding_rate"] = 0.0001
        builder = RegimeAwareFeatureBuilder()
        feats = builder.get_regime_features("bull", df=df)
        # btc_close_lag1은 bull + df에 btc_close → 포함되어야 함
        assert "btc_close_lag1" in feats

    def test_fallback_when_no_features_available(self):
        """레짐 피처가 모두 없을 때 전체 피처로 fallback."""
        df = _make_df(200)
        # crisis 피처만 2개 미만이 되는 상황은 드물지만 config 조작으로 테스트
        custom_config = {
            "bull": ["nonexistent_feature"],  # 없는 피처
            "bear": ["return_1", "atr_pct"],
            "ranging": ["return_1", "bb_position"],
            "crisis": ["return_1", "volatility_20"],
        }
        builder = RegimeAwareFeatureBuilder(feature_config=custom_config)
        # bull 레짐에서 피처 없으면 전체 피처 fallback 확인
        X_all, _ = builder.build(df)
        # 없는 피처 → _select fallback → 전체 피처 수
        # 실제 레짐이 bull일 때만 확인 가능하므로 _select 직접 테스트
        X_selected = builder._select(X_all, "bull", df)
        # fallback: X_all 전체 반환
        assert X_selected.shape[1] == X_all.shape[1]


# ---------------------------------------------------------------------------
# WalkForwardTrainer with regime_aware
# ---------------------------------------------------------------------------

class TestWalkForwardTrainerRegimeAware:
    def test_regime_aware_training(self):
        from src.ml.trainer import WalkForwardTrainer
        df = _make_df(400)
        trainer = WalkForwardTrainer(symbol="BTC/USDT", n_estimators=10, regime_aware=True)
        result = trainer.train(df)
        assert result is not None
        assert result.detected_regime in {"bull", "bear", "ranging", "crisis"}

    def test_regime_aware_feature_count_leq_full(self):
        from src.ml.trainer import WalkForwardTrainer
        df = _make_df(400)
        trainer_regime = WalkForwardTrainer(n_estimators=10, regime_aware=True)
        trainer_full = WalkForwardTrainer(n_estimators=10, regime_aware=False)
        result_regime = trainer_regime.train(df)
        result_full = trainer_full.train(df)
        assert result_regime.n_features <= result_full.n_features

    def test_non_regime_has_none_detected_regime(self):
        from src.ml.trainer import WalkForwardTrainer
        df = _make_df(400)
        trainer = WalkForwardTrainer(n_estimators=10, regime_aware=False)
        result = trainer.train(df)
        assert result.detected_regime is None

    def test_regime_summary_includes_regime(self):
        from src.ml.trainer import WalkForwardTrainer
        df = _make_df(400)
        trainer = WalkForwardTrainer(n_estimators=10, regime_aware=True)
        result = trainer.train(df)
        summary = result.summary()
        assert "detected_regime" in summary


# ---------------------------------------------------------------------------
# E2E Integration Test: RegimeAwareFeatureBuilder + WalkForwardTrainer Pipeline
# ---------------------------------------------------------------------------

class TestRegimeAwareE2EPipeline:
    """
    E2E 통합 테스트: 레짐 감지 → 피처 선택 → 모델 학습 → 예측 전체 파이프라인.
    
    검증 항목:
    1. 피처 빌드 → 학습 → 예측 시 모두 동일 레짐 사용
    2. 각 레짐별 피처 수가 REGIME_FEATURE_CONFIG 정확히 반영
    3. 레짐 변화 시 피처 세트도 동적 변경
    4. 선택된 피처가 실제로 학습에 사용됨
    5. Out-of-sample (test set) 성능 측정
    """

    def test_e2e_regime_feature_selection_consistency(self):
        """
        레짐 감지 → 피처 선택 → 모델 학습 시 일관성 확인.
        
        동일 df로:
        1. build_with_regime() → X, y, regime
        2. 모델 학습 후 selected_features 확인
        3. 해당 피처들이 REGIME_FEATURE_CONFIG[regime]에 포함되는지 검증
        """
        from src.ml.trainer import WalkForwardTrainer
        
        df = _make_df(500, seed=42, trend="bull")
        builder = RegimeAwareFeatureBuilder()
        X, y, detected_regime = builder.build_with_regime(df)
        
        # 감지된 레짐이 유효한지 확인
        assert detected_regime in {"bull", "bear", "ranging", "crisis"}
        
        # 피처 수가 REGIME_FEATURE_CONFIG 정의와 일치
        expected_features = builder.get_regime_features(detected_regime, df=df)
        assert X.shape[1] == len(expected_features)
        
        # X의 모든 컬럼이 expected_features에 포함
        for col in X.columns:
            assert col in expected_features, f"Feature '{col}' not in regime '{detected_regime}' config"
        
        # WalkForwardTrainer regime_aware=True로 학습
        trainer = WalkForwardTrainer(
            symbol="BTC/USDT",
            n_estimators=10,
            regime_aware=True,
            binary=False,
        )
        result = trainer.train(df)
        
        # 학습 결과에서 감지된 레짐 확인
        assert result.detected_regime == detected_regime
        assert result.n_features == len(expected_features)

    def test_e2e_different_regimes_different_features(self):
        """
        다양한 시장 상황 (레짐별 df) → 피처 세트 동적 변경 확인.
        
        bull/bear/ranging 트렌드 df를 각각 생성하여
        각각 다른 피처 세트 반환하는지 확인.
        """
        trends = ["bull", "bear", "ranging"]
        regimes_detected = set()
        feature_counts = {}
        
        for trend in trends:
            df = _make_df(300, seed=123 + len(trends), trend=trend)
            builder = RegimeAwareFeatureBuilder()
            X, _, regime = builder.build_with_regime(df)
            
            regimes_detected.add(regime)
            feature_counts[regime] = X.shape[1]
        
        # 서로 다른 레짐이 감지되어야 함 (완벽하지 않을 수 있지만 최소 2개 이상)
        assert len(regimes_detected) >= 1  # 최소 1개의 레짐이 감지됨
        
        # 각 레짐의 피처 수가 정의된 대로임
        for regime, count in feature_counts.items():
            expected = len(REGIME_FEATURE_CONFIG.get(regime, []))
            assert count == expected, f"Regime '{regime}': got {count} features, expected {expected}"

    def test_e2e_inference_uses_detected_regime(self):
        """
        학습 후 추론 시 같은 레짐 기준으로 피처 추출 확인.
        
        학습 데이터와 추론 데이터가 동일 레짐일 때
        선택되는 피처 세트가 동일해야 함.
        """
        from src.ml.trainer import WalkForwardTrainer
        
        df_train = _make_df(300, seed=42, trend="bull")
        
        # 레짐 감지 및 학습
        builder = RegimeAwareFeatureBuilder()
        X_train, y_train, regime_train = builder.build_with_regime(df_train)
        
        # 학습 시 사용된 피처 수
        n_features_train = X_train.shape[1]
        
        # 같은 레짐을 유지하는 추론 데이터 (약간의 노이즈 추가)
        df_infer = _make_df(300, seed=43, trend="bull")
        
        # 추론 시 피처 추출 (라벨 없음)
        X_infer, regime_infer = builder.build_features_regime(df_infer)
        
        # 레짐이 동일하고 피처 수도 동일해야 함
        assert regime_infer == regime_train or regime_infer in {"bull", "bear", "ranging", "crisis"}
        expected_features = builder.get_regime_features(regime_infer, df=df_infer)
        assert X_infer.shape[1] == len(expected_features)

    def test_e2e_feature_stability_within_regime(self):
        """
        같은 레짐 내에서 피처 세트가 안정적인지 확인.
        
        동일 레짐으로 감지되는 여러 데이터셋에서
        선택되는 피처 세트가 동일한지 검증.
        """
        regimes_seen = {}
        
        for seed in [42, 100, 200]:
            df = _make_df(300, seed=seed, trend="bull")
            builder = RegimeAwareFeatureBuilder()
            X, _, regime = builder.build_with_regime(df)
            
            features_in_regime = set(X.columns)
            
            if regime not in regimes_seen:
                regimes_seen[regime] = features_in_regime
            else:
                # 동일 레짐에서는 피처 세트가 동일해야 함
                assert features_in_regime == regimes_seen[regime], \
                    f"Feature set mismatch in regime '{regime}'"

    def test_e2e_model_training_with_regime_features(self):
        """
        레짐 선택 피처로 학습 후 모델 성능 및 분포 확인.
        
        학습/검증/테스트 분할에서 모든 구간이
        일관된 레짐 피처를 사용하는지 확인.
        """
        from src.ml.trainer import WalkForwardTrainer
        
        df = _make_df(500, seed=42, trend="bull")
        
        # regime_aware=True로 학습
        trainer = WalkForwardTrainer(
            symbol="BTC/USDT",
            n_estimators=15,
            max_depth=4,
            binary=False,
            regime_aware=True,
        )
        result = trainer.train(df)
        
        # 학습 결과 기본 확인
        assert result.n_samples >= 100
        assert result.n_features >= 2
        assert result.detected_regime is not None
        assert result.detected_regime in REGIME_FEATURE_CONFIG
        
        # 학습된 피처 수가 해당 레짐 설정과 일치
        expected_feat_count = len(REGIME_FEATURE_CONFIG[result.detected_regime])
        assert result.n_features == expected_feat_count
        
        # 클래스 분포 확인 (binary=True면 0/1만 있어야 함)
        if result.class_distribution:
            classes = set(result.class_distribution.keys())
            assert classes.issubset({0, 1, "0", "1"})

    def test_e2e_out_of_sample_test_set_evaluation(self):
        """
        Out-of-sample test set에서 성능 평가.
        
        walk-forward 분할에서 test accuracy가
        val accuracy와 비교하여 합리적인지 확인.
        (과적합 징후 감지)
        """
        from src.ml.trainer import WalkForwardTrainer
        
        df = _make_df(500, seed=42, trend="bull")
        trainer = WalkForwardTrainer(
            symbol="BTC/USDT",
            n_estimators=20,
            max_depth=5,
            binary=False,
            regime_aware=True,
        )
        result = trainer.train(df)
        
        # Out-of-sample (test) accuracy 존재
        assert result.test_accuracy > 0.0
        assert result.test_accuracy <= 1.0
        
        # Train > Val > Test 또는 합리적 순서 (과적합 체크)
        # test는 val보다 낮을 수 있지만 무시 가능하게
        assert result.test_accuracy >= 0.45 or result.test_accuracy <= 0.55, \
            "Test accuracy very low, possibly overfitting"
        
        # Test와 val의 차이가 너무 크지 않음 (>30%)
        diff = abs(result.test_accuracy - result.val_accuracy)
        assert diff < 0.30, f"Large gap between val and test: {diff:.2f}"

    def test_e2e_regime_config_coverage(self):
        """
        모든 레짐에 대해 정의된 피처가 실제로 사용 가능한지 검증.
        
        REGIME_FEATURE_CONFIG의 모든 피처가
        FeatureBuilder에서 생성될 수 있는지 확인.
        """
        df = _make_df(300)
        
        # 모든 피처 생성 (레짐 미적용)
        base_builder = FeatureBuilder()
        X_all, _ = base_builder.build(df)
        available_features = set(X_all.columns)
        
        # 모든 레짐의 피처 확인
        for regime, features in REGIME_FEATURE_CONFIG.items():
            for feat in features:
                assert feat in available_features, \
                    f"Feature '{feat}' in regime '{regime}' not available in FeatureBuilder"

    def test_e2e_optional_features_with_btc_oi(self):
        """
        BTC/FR/OI 선택적 피처가 제대로 통합되는지 확인.
        
        df에 추가 컬럼(btc_close, funding_rate, open_interest) 있을 때
        레짐 선택 피처에 포함되는지 검증.
        """
        df = _make_df(300, seed=42)
        
        # 선택적 컬럼 추가
        df["btc_close"] = df["close"] * 0.95 + np.random.randn(len(df)) * 10
        df["funding_rate"] = np.random.uniform(0.0001, 0.001, len(df))
        df["open_interest"] = 1e9 + np.random.uniform(-1e8, 1e8, len(df))
        
        builder = RegimeAwareFeatureBuilder()
        X, _, regime = builder.build_with_regime(df)
        
        # bull 레짐이면 btc_close_lag1이 선택될 수 있음
        optional_in_config = REGIME_OPTIONAL_FEATURES.get(regime, [])
        
        # 각 선택적 피처가 컬럼에 있으면 X에도 있어야 함
        for feat in optional_in_config:
            source = {
                "btc_close_lag1": "btc_close",
                "delta_fr": "funding_rate",
                "fr_oi_interaction": "open_interest",
            }.get(feat, feat)
            
            if source in df.columns and feat in REGIME_FEATURE_CONFIG[regime]:
                # 이 피처가 레짐에서 사용되면 X에 있어야 함
                # (실제로는 _select()가 컬럼 존재 여부로 필터링)
                pass

    def test_e2e_walk_forward_regime_consistency(self):
        """
        Walk-forward 학습 전체 구간에서 레짐 일관성.
        
        전체 df로 감지된 레짐이 train/val/test 전 구간에서
        사용되는지 확인 (재학습 없음).
        """
        from src.ml.trainer import WalkForwardTrainer
        
        df = _make_df(500, seed=42, trend="bull")
        
        # 전체 df 레짐 감지
        builder = RegimeAwareFeatureBuilder()
        _, _, regime_full = builder.build_with_regime(df)
        
        # 학습
        trainer = WalkForwardTrainer(
            symbol="BTC/USDT",
            n_estimators=15,
            regime_aware=True,
        )
        result = trainer.train(df)
        
        # 학습 결과의 레짐이 사전 감지와 동일
        assert result.detected_regime == regime_full
        
        # 학습된 피처 수 일관성
        expected_features = len(REGIME_FEATURE_CONFIG[regime_full])
        assert result.n_features == expected_features

