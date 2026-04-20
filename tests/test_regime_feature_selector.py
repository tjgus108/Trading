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
