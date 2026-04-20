"""
FeatureBuilder 단위 테스트.

src/ml/features.py 핵심 로직 커버:
  - build() 출력 형태 및 피처 컬럼
  - build_features_only() (추론 전용)
  - feature_names 속성
  - 3-class / binary / triple_barrier 레이블
  - 선택적 피처 (btc_close_lag1, delta_fr, fr_oi_interaction)
  - EMA/ATR 컬럼 유무에 따른 분기
  - 엣지케이스 (짧은 데이터, 상수 가격)
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.features import FeatureBuilder


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _make_ohlcv(n: int = 100, seed: int = 42) -> pd.DataFrame:
    """기본 OHLCV DataFrame 생성."""
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    close = np.clip(close, 1.0, None)
    high = close * (1 + rng.uniform(0, 0.01, n))
    low = close * (1 - rng.uniform(0, 0.01, n))
    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": rng.uniform(1000, 5000, n),
    })


# ── build() 기본 동작 ────────────────────────────────────────────────────────


class TestBuildBasic:
    """build() 출력 형태, 컬럼, NaN 제거 검증."""

    def test_output_shapes_match(self):
        """X 행수 == y 행수."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert len(X) == len(y)
        assert len(X) > 0

    def test_no_nan_in_output(self):
        """build() 결과에 NaN 없어야 함."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert not X.isna().any().any()
        assert not y.isna().any()

    def test_base_feature_columns_present(self):
        """기본 14개 피처 컬럼 모두 존재."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        for col in fb.feature_names:
            assert col in X.columns, f"Missing feature: {col}"

    def test_no_inf_in_features(self):
        """피처에 inf 없어야 함."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()


# ── build_features_only() ─────────────────────────────────────────────────────


class TestBuildFeaturesOnly:
    """추론 전용 피처 생성."""

    def test_returns_dataframe_without_label(self):
        """레이블 없이 피처만 반환."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert isinstance(X, pd.DataFrame)
        assert "label" not in X.columns

    def test_no_nan(self):
        """NaN 제거됨."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert not X.isna().any().any()

    def test_has_base_features(self):
        """기본 피처 컬럼 포함."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        for col in fb.feature_names:
            assert col in X.columns


# ── feature_names 속성 ────────────────────────────────────────────────────────


class TestFeatureNames:
    """feature_names property 검증."""

    def test_returns_14_base_features(self):
        """기본 피처 14개."""
        fb = FeatureBuilder()
        assert len(fb.feature_names) == 14

    def test_no_removed_features(self):
        """Cycle 149에서 제거된 피처 포함되지 않음."""
        fb = FeatureBuilder()
        removed = ["rsi14", "rsi_zscore", "price_vs_vwap"]
        for name in removed:
            assert name not in fb.feature_names


# ── 3-class 레이블 (기본 모드) ─────────────────────────────────────────────────


class TestThreeClassLabels:
    """기본 3-class 레이블: BUY(1) / SELL(-1) / HOLD(0)."""

    def test_label_values_in_expected_set(self):
        """레이블 값이 {-1, 0, 1} 중 하나."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder(threshold=0.001)
        X, y = fb.build(df)
        unique = set(y.dropna().unique())
        assert unique.issubset({-1, 0, 1})

    def test_custom_threshold_affects_label_distribution(self):
        """threshold가 클수록 HOLD 비율 증가."""
        df = _make_ohlcv(200, seed=10)
        fb_small = FeatureBuilder(threshold=0.001)
        fb_large = FeatureBuilder(threshold=0.05)
        _, y_small = fb_small.build(df)
        _, y_large = fb_large.build(df)
        # 큰 threshold → HOLD(0) 비율 증가
        hold_ratio_small = (y_small == 0).sum() / len(y_small)
        hold_ratio_large = (y_large == 0).sum() / len(y_large)
        assert hold_ratio_large >= hold_ratio_small

    def test_forward_n_parameter(self):
        """forward_n 변경 시 결과 행 수 변화."""
        df = _make_ohlcv(100)
        fb_5 = FeatureBuilder(forward_n=5)
        fb_10 = FeatureBuilder(forward_n=10)
        X5, _ = fb_5.build(df)
        X10, _ = fb_10.build(df)
        # forward_n이 클수록 마지막 N개 바의 레이블이 NaN → 유효 행 수 감소
        assert len(X5) >= len(X10)


# ── Binary 모드 레이블 ────────────────────────────────────────────────────────


class TestBinaryLabels:
    """binary=True: 2-class (UP=1 / DOWN=0), 중립 구간 제거."""

    def test_binary_labels_only_0_and_1(self):
        """binary 모드에서 레이블은 0 또는 1만."""
        df = _make_ohlcv(200, seed=7)
        fb = FeatureBuilder(binary=True, binary_threshold=0.001)
        X, y = fb.build(df)
        unique = set(y.dropna().unique())
        assert unique.issubset({0, 1})

    def test_binary_removes_neutral_zone(self):
        """binary_threshold 이내 → NaN으로 제거됨 → 행 수 감소."""
        df = _make_ohlcv(200, seed=7)
        fb_3class = FeatureBuilder(threshold=0.001)
        fb_binary = FeatureBuilder(binary=True, binary_threshold=0.01)
        X_3, _ = fb_3class.build(df)
        X_bin, _ = fb_binary.build(df)
        # binary는 중립 구간 제거 → 행 수 같거나 적음
        assert len(X_bin) <= len(X_3)


# ── Triple Barrier 레이블 ─────────────────────────────────────────────────────


class TestTripleBarrierLabels:
    """triple_barrier=True + binary=True: TP/SL 배리어 기반 레이블."""

    def test_triple_barrier_labels_0_or_1(self):
        """triple barrier 레이블은 0 또는 1."""
        df = _make_ohlcv(200, seed=3)
        fb = FeatureBuilder(
            binary=True, triple_barrier=True,
            tb_tp_pct=0.02, tb_sl_pct=0.01,
        )
        X, y = fb.build(df)
        unique = set(y.dropna().unique())
        assert unique.issubset({0, 1})

    def test_triple_barrier_requires_binary(self):
        """binary=False + triple_barrier=True → 일반 3-class 레이블 사용."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder(binary=False, triple_barrier=True)
        X, y = fb.build(df)
        # triple_barrier는 binary=True일 때만 적용 → 3-class로 fallback
        unique = set(y.dropna().unique())
        assert unique.issubset({-1, 0, 1})

    def test_triple_barrier_tight_barriers_more_labels(self):
        """작은 TP/SL 배리어 → 더 많은 배리어 터치 → NaN 감소."""
        df = _make_ohlcv(200, seed=5)
        fb_tight = FeatureBuilder(
            binary=True, triple_barrier=True,
            tb_tp_pct=0.005, tb_sl_pct=0.005, forward_n=10,
        )
        fb_wide = FeatureBuilder(
            binary=True, triple_barrier=True,
            tb_tp_pct=0.10, tb_sl_pct=0.10, forward_n=10,
        )
        X_tight, _ = fb_tight.build(df)
        X_wide, _ = fb_wide.build(df)
        # 좁은 배리어 → 더 많은 레이블 생성 (시간 초과 NaN 감소)
        assert len(X_tight) >= len(X_wide)


# ── 선택적 피처: BTC lag ──────────────────────────────────────────────────────


class TestBtcLagFeature:
    """df에 btc_close 컬럼이 있을 때 btc_close_lag1 피처 추가."""

    def test_btc_lag_added_when_column_exists(self):
        """btc_close 있으면 btc_close_lag1 피처 생성."""
        df = _make_ohlcv(100)
        df["btc_close"] = df["close"] * 500  # BTC 가격
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "btc_close_lag1" in X.columns

    def test_btc_lag_not_added_without_column(self):
        """btc_close 없으면 btc_close_lag1 미생성."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "btc_close_lag1" not in X.columns


# ── 선택적 피처: FR/OI ────────────────────────────────────────────────────────


class TestFrOiFeatures:
    """funding_rate / open_interest 기반 파생 피처."""

    def test_delta_fr_added(self):
        """funding_rate 있으면 delta_fr 추가."""
        df = _make_ohlcv(100)
        df["funding_rate"] = np.random.default_rng(42).uniform(-0.001, 0.001, 100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "delta_fr" in X.columns

    def test_fr_oi_interaction_added(self):
        """funding_rate + open_interest 있으면 fr_oi_interaction 추가."""
        df = _make_ohlcv(100)
        rng = np.random.default_rng(42)
        df["funding_rate"] = rng.uniform(-0.001, 0.001, 100)
        df["open_interest"] = rng.uniform(1e6, 1e7, 100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "fr_oi_interaction" in X.columns

    def test_no_fr_columns_no_features(self):
        """FR/OI 컬럼 없으면 관련 피처 미생성."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "delta_fr" not in X.columns
        assert "fr_oi_interaction" not in X.columns


# ── EMA / ATR 분기 테스트 ─────────────────────────────────────────────────────


class TestFeatureBranches:
    """ema20/ema50 또는 atr14 컬럼 유무에 따른 분기 동작."""

    def test_with_ema_columns(self):
        """ema20/ema50 컬럼 있으면 해당 값 사용."""
        df = _make_ohlcv(100)
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "ema_ratio" in X.columns
        assert not X["ema_ratio"].isna().any()

    def test_without_ema_columns_still_computes(self):
        """ema 컬럼 없어도 자체 계산으로 피처 생성."""
        df = _make_ohlcv(100)
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "ema_ratio" in X.columns

    def test_with_atr14_column(self):
        """atr14 컬럼 있으면 해당 값 사용."""
        df = _make_ohlcv(100)
        prev_close = df["close"].shift(1)
        tr = pd.concat([
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ], axis=1).max(axis=1)
        df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "atr_pct" in X.columns

    def test_with_donchian_columns(self):
        """donchian_high/low 컬럼 있으면 해당 값 사용."""
        df = _make_ohlcv(100)
        df["donchian_high"] = df["high"].rolling(20).max()
        df["donchian_low"] = df["low"].rolling(20).min()
        fb = FeatureBuilder()
        X = fb.build_features_only(df)
        assert "donchian_pct" in X.columns
        assert not X["donchian_pct"].isna().any()


# ── 엣지케이스 ────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """경계 조건 및 비정상 입력 처리."""

    def test_constant_price_no_crash(self):
        """가격이 모두 동일해도 예외 없이 동작."""
        n = 100
        df = pd.DataFrame({
            "open": np.full(n, 100.0),
            "high": np.full(n, 100.5),
            "low": np.full(n, 99.5),
            "close": np.full(n, 100.0),
            "volume": np.full(n, 1000.0),
        })
        fb = FeatureBuilder()
        X, y = fb.build(df)
        assert not np.isinf(X.values).any()

    def test_short_dataframe_no_crash(self):
        """데이터가 짧아도 예외 없이 동작 (행 수 0 가능)."""
        df = _make_ohlcv(30)
        fb = FeatureBuilder(forward_n=5)
        X, y = fb.build(df)
        # 피처 계산에 ~20바 warming 필요 → 유효 행 적을 수 있음
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)

    def test_init_defaults(self):
        """기본 생성자 파라미터 검증."""
        fb = FeatureBuilder()
        assert fb.forward_n == 5
        assert fb.threshold == 0.003
        assert fb.binary is False
        assert fb.triple_barrier is False
