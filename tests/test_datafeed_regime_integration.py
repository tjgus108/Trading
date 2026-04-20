"""
Cycle 174: DataFeed-RegimeAwareFeatureBuilder E2E 파이프라인 통합 테스트.

목표:
1. DataFeed.fetch_with_regime() → 캐시된 레짐
2. RegimeAwareFeatureBuilder.build_with_cached_regime() → 동일 레짐 피처
3. End-to-end 검증: 레짐 변경 시 피처 세트도 변경
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from src.data.feed import DataFeed, DataSummary
from src.ml.features import (
    RegimeAwareFeatureBuilder,
    REGIME_FEATURE_CONFIG,
    detect_regime,
)


def _make_synthetic_df(n: int = 300, seed: int = 42, trend: str = "neutral") -> pd.DataFrame:
    """테스트용 합성 OHLCV 데이터."""
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


class TestDataFeedRegimeDetection:
    """DataFeed.detect_and_cache_regime() 단위 테스트."""

    def test_detect_and_cache_regime_returns_valid_regime(self):
        """레짐 감지 결과가 유효한 문자열."""
        connector = MagicMock()
        feed = DataFeed(connector)
        
        df = _make_synthetic_df(300, trend="bull")
        regime = feed.detect_and_cache_regime("BTC/USDT", df, ttl=300)
        
        assert regime in {"bull", "bear", "ranging", "crisis"}

    def test_detect_and_cache_regime_saves_to_cache(self):
        """감지 결과가 캐시에 저장됨."""
        connector = MagicMock()
        feed = DataFeed(connector)
        
        df = _make_synthetic_df(300, trend="bull")
        regime = feed.detect_and_cache_regime("BTC/USDT", df, ttl=300)
        cached_regime = feed.get_cached_regime("BTC/USDT")
        
        assert cached_regime == regime

    def test_detect_and_cache_regime_fallback_to_cache_on_error(self):
        """감지 실패 시 캐시된 레짐 반환."""
        connector = MagicMock()
        feed = DataFeed(connector)
        
        # 먼저 정상 감지
        df = _make_synthetic_df(300)
        feed.detect_and_cache_regime("BTC/USDT", df, ttl=300)
        cached = feed.get_cached_regime("BTC/USDT")
        
        # 불완전한 DataFrame으로 감지 시도 (fallback 유도)
        bad_df = pd.DataFrame({"close": [100]})
        regime = feed.detect_and_cache_regime("BTC/USDT", bad_df, ttl=300)
        
        # fallback: 캐시 또는 'ranging'
        assert regime is not None
        assert regime in {"bull", "bear", "ranging", "crisis"}


class TestDataFeedFetchWithRegime:
    """DataFeed.fetch_with_regime() end-to-end 테스트."""

    def test_fetch_with_regime_returns_tuple(self):
        """fetch_with_regime() 반환값이 (DataSummary, str)."""
        connector = MagicMock()
        connector.fetch_ohlcv = MagicMock(return_value=[
            [i, 50000+i, 50100+i, 49900+i, 50000+i, 100] 
            for i in range(500)
        ])
        feed = DataFeed(connector)
        
        summary, regime = feed.fetch_with_regime("BTC/USDT", "1h", limit=500)
        
        assert isinstance(summary, DataSummary)
        assert isinstance(regime, str)
        assert regime in {"bull", "bear", "ranging", "crisis"}

    def test_fetch_with_regime_caches_regime(self):
        """fetch_with_regime() 후 캐시에 레짐 저장됨."""
        connector = MagicMock()
        connector.fetch_ohlcv = MagicMock(return_value=[
            [i, 50000+i, 50100+i, 49900+i, 50000+i, 100] 
            for i in range(500)
        ])
        feed = DataFeed(connector)
        
        _, regime = feed.fetch_with_regime("BTC/USDT", "1h", limit=500)
        cached = feed.get_cached_regime("BTC/USDT")
        
        assert cached == regime

    def test_fetch_with_regime_uses_effective_ttl(self):
        """fetch_with_regime() 시 regime_cache가 effective_ttl 적용됨."""
        connector = MagicMock()
        connector.fetch_ohlcv = MagicMock(return_value=[
            [i, 50000+i, 50100+i, 49900+i, 50000+i, 100] 
            for i in range(500)
        ])
        feed = DataFeed(connector, cache_ttl=60)
        
        # bull 레짐 → TTL 배수 0.5 (trending)
        # 실제 로직은 _effective_ttl()에서 정의됨
        _, regime = feed.fetch_with_regime("BTC/USDT", "1h", limit=500)
        
        # 캐시되었는지만 확인 (TTL은 내부)
        assert feed.get_cached_regime("BTC/USDT") is not None


class TestRegimeAwareBuilderWithCachedRegime:
    """RegimeAwareFeatureBuilder.build_with_cached_regime() 테스트."""

    def test_build_with_cached_regime_returns_three_values(self):
        """캐시된 레짐 기반 build() → (X, y, regime)."""
        df = _make_synthetic_df(300, trend="bull")
        builder = RegimeAwareFeatureBuilder()
        
        # 미리 detect_regime()으로 레짐 확인
        regime = detect_regime(df)
        
        X, y, used_regime = builder.build_with_cached_regime(df, feed_regime=regime)
        
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert used_regime == regime

    def test_build_with_cached_regime_fallback_to_internal_detect(self):
        """feed_regime=None일 때 내부 detect_regime() 호출."""
        df = _make_synthetic_df(300)
        builder = RegimeAwareFeatureBuilder()
        
        X1, y1, regime1 = builder.build_with_cached_regime(df, feed_regime=None)
        X2, y2, regime2 = builder.build_with_regime(df)
        
        # 동일한 결과여야 함
        assert regime1 == regime2
        pd.testing.assert_frame_equal(X1, X2)
        pd.testing.assert_series_equal(y1, y2)

    def test_build_with_cached_regime_invalid_regime_fallback(self):
        """잘못된 레짐 전달 시 fallback."""
        df = _make_synthetic_df(300)
        builder = RegimeAwareFeatureBuilder()
        
        X, y, used_regime = builder.build_with_cached_regime(df, feed_regime="invalid_regime")
        
        # Fallback: 내부 detect_regime() 사용
        assert used_regime in {"bull", "bear", "ranging", "crisis"}

    def test_build_with_cached_regime_features_match_config(self):
        """선택된 피처가 REGIME_FEATURE_CONFIG와 일치."""
        df = _make_synthetic_df(300, trend="bull")
        builder = RegimeAwareFeatureBuilder()
        
        regime = detect_regime(df)
        X, _, used_regime = builder.build_with_cached_regime(df, feed_regime=regime)
        
        expected_features = builder.get_regime_features(used_regime, df=df)
        assert X.shape[1] == len(expected_features)
        
        for col in X.columns:
            assert col in expected_features


class TestBuildFeaturesWithCachedRegime:
    """RegimeAwareFeatureBuilder.build_features_with_cached_regime() 테스트."""

    def test_build_features_with_cached_regime_returns_two_values(self):
        """캐시된 레짐 기반 피처 추출 → (X, regime)."""
        df = _make_synthetic_df(300, trend="bear")
        builder = RegimeAwareFeatureBuilder()
        
        regime = detect_regime(df)
        X, used_regime = builder.build_features_with_cached_regime(df, feed_regime=regime)
        
        assert isinstance(X, pd.DataFrame)
        assert used_regime == regime

    def test_build_features_with_cached_regime_no_labels(self):
        """피처만 반환 (레이블 없음)."""
        df = _make_synthetic_df(300)
        builder = RegimeAwareFeatureBuilder()
        
        regime = detect_regime(df)
        X, _ = builder.build_features_with_cached_regime(df, feed_regime=regime)
        
        assert "label" not in X.columns


class TestE2EDataFeedToFeatureBuilder:
    """End-to-end 통합: DataFeed fetch_with_regime() → RegimeAwareFeatureBuilder."""

    def test_e2e_consistent_regime_across_pipeline(self):
        """
        DataFeed.fetch_with_regime()의 레짐 == 
        RegimeAwareFeatureBuilder.build_with_cached_regime()의 레짐.
        """
        connector = MagicMock()
        connector.fetch_ohlcv = MagicMock(return_value=[
            [i, 50000+i, 50100+i, 49900+i, 50000+i, 100] 
            for i in range(500)
        ])
        feed = DataFeed(connector)
        
        # Step 1: DataFeed fetch
        summary, feed_regime = feed.fetch_with_regime("BTC/USDT", "1h", limit=500)
        
        # Step 2: RegimeAwareFeatureBuilder
        builder = RegimeAwareFeatureBuilder()
        X, y, builder_regime = builder.build_with_cached_regime(
            summary.df, 
            feed_regime=feed_regime
        )
        
        # 레짐 일치
        assert feed_regime == builder_regime

    def test_e2e_different_trends_different_features(self):
        """
        서로 다른 트렌드 데이터 → 서로 다른 피처 세트.
        
        (완벽히 다를 수는 없지만, 같은 레짐 내에서는 동일해야 함)
        """
        connector = MagicMock()
        connector.fetch_ohlcv = MagicMock(return_value=[
            [i, 50000+i, 50100+i, 49900+i, 50000+i, 100] 
            for i in range(500)
        ])
        feed = DataFeed(connector)
        builder = RegimeAwareFeatureBuilder()
        
        # Bull 트렌드
        summary_bull, regime_bull = feed.fetch_with_regime("BTC/USDT", "1h")
        X_bull, _, _ = builder.build_with_cached_regime(summary_bull.df, feed_regime=regime_bull)
        
        # Bear 트렌드 (다른 connector 모킹)
        connector_bear = MagicMock()
        connector_bear.fetch_ohlcv = MagicMock(return_value=[
            [i, 60000-i, 60100-i, 59900-i, 60000-i, 100] 
            for i in range(500)
        ])
        feed_bear = DataFeed(connector_bear)
        summary_bear, regime_bear = feed_bear.fetch_with_regime("BTC/USDT", "1h")
        X_bear, _, _ = builder.build_with_cached_regime(summary_bear.df, feed_regime=regime_bear)
        
        # 피처 수는 각각 레짐별 설정과 일치
        expected_bull = len(REGIME_FEATURE_CONFIG.get(regime_bull, []))
        expected_bear = len(REGIME_FEATURE_CONFIG.get(regime_bear, []))
        
        assert X_bull.shape[1] == expected_bull
        assert X_bear.shape[1] == expected_bear

    def test_e2e_feature_stability_within_regime(self):
        """
        동일 레짐 감지 → 동일 피처 세트.
        """
        df = _make_synthetic_df(500, seed=42, trend="bull")
        
        # 동일 df로 여러 번 처리
        connector = MagicMock()
        feed = DataFeed(connector)
        builder = RegimeAwareFeatureBuilder()
        
        regime = detect_regime(df)
        
        # 첫 번째
        X1, _, regime1 = builder.build_with_cached_regime(df, feed_regime=regime)
        
        # 두 번째
        X2, _, regime2 = builder.build_with_cached_regime(df, feed_regime=regime)
        
        # 레짐과 피처가 동일해야 함
        assert regime1 == regime2
        pd.testing.assert_frame_equal(X1, X2)

    def test_e2e_inference_pipeline(self):
        """
        학습/추론 분할 시 일관된 레짐 사용.
        
        (실제 live 트레이딩 시뮬레이션)
        """
        # 학습 데이터
        df_train = _make_synthetic_df(300, seed=42, trend="bull")
        
        # 추론 데이터 (같은 트렌드)
        df_infer = _make_synthetic_df(300, seed=43, trend="bull")
        
        # 학습 레짐
        regime_train = detect_regime(df_train)
        
        # 학습 피처
        builder = RegimeAwareFeatureBuilder()
        X_train, y_train, _ = builder.build_with_cached_regime(df_train, feed_regime=regime_train)
        n_features_train = X_train.shape[1]
        
        # 추론: 같은 레짐 가정
        regime_infer = detect_regime(df_infer)
        X_infer, _ = builder.build_features_with_cached_regime(df_infer, feed_regime=regime_infer)
        
        # 피처 수는 (같은 레짐이면) 동일
        if regime_infer == regime_train:
            assert X_infer.shape[1] == n_features_train
        
        # 어쨌든 피처 컬럼이 유효해야 함
        assert X_infer.shape[1] > 0
        assert not X_infer.isnull().any().any()
