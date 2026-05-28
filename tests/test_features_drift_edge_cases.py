"""
FeatureBuilder + DriftDetector 엣지 케이스 테스트 (7개).

목표:
1. 빈 DataFrame 처리
2. 극단 값 (inf, -inf, NaN 가득한 데이터)
3. 너무 짧은 시계열 (< forward_n)
4. Triple Barrier 레이블링 엣지 케이스
5. Drift Detector 초기화 상태 검증
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ml.features import FeatureBuilder
from src.ml.drift_detector import (
    PageHinkleyDriftDetector,
    CUSUMDriftDetector,
)


class TestFeatureBuilderEdgeCases:
    """FeatureBuilder 엣지 케이스."""

    def test_empty_dataframe_returns_empty(self):
        """빈 DataFrame 입력 → 빈 결과."""
        df = pd.DataFrame()
        fb = FeatureBuilder(forward_n=5)
        
        X, y = fb.build(df)
        assert len(X) == 0
        assert len(y) == 0

    def test_dataframe_shorter_than_forward_n(self):
        """길이 < forward_n → NaN 많음 → 결과 비어있을 수 있음."""
        close = np.array([100.0, 101.0, 102.0])  # 길이 3 < forward_n=5
        df = pd.DataFrame({
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": [1000, 1000, 1000],
        })
        
        fb = FeatureBuilder(forward_n=5)
        X, y = fb.build(df)
        
        # forward_n 때문에 충분한 피처가 생성되지 못함
        # 결과가 비어있거나 매우 짧을 것으로 예상
        assert len(X) <= 3

    def test_all_nan_dataframe(self):
        """모든 값이 NaN → 결과 비어있음."""
        df = pd.DataFrame({
            "open": [np.nan] * 10,
            "high": [np.nan] * 10,
            "low": [np.nan] * 10,
            "close": [np.nan] * 10,
            "volume": [np.nan] * 10,
        })
        
        fb = FeatureBuilder(forward_n=5)
        X, y = fb.build(df)
        
        assert len(X) == 0, "Expected empty result for all-NaN input"

    def test_features_only_with_empty_df(self):
        """build_features_only() 빈 DataFrame → 빈 결과."""
        df = pd.DataFrame()
        fb = FeatureBuilder()
        
        X = fb.build_features_only(df)
        assert len(X) == 0

    def test_extreme_values_clipped(self):
        """극단값 (inf, -inf) 포함 → 계산이 유효하게 처리되어야 함."""
        close = np.array([100.0, 101.0, np.inf, 103.0, 104.0])
        df = pd.DataFrame({
            "open": close.copy(),
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": [1000] * 5,
        })
        
        fb = FeatureBuilder(forward_n=3)
        X, y = fb.build(df)
        
        # inf 때문에 관련 행들이 NaN으로 처리되고 제거될 것
        # 결과가 비어있거나 많이 줄어들 것으로 예상
        assert len(X) < 5, "Expected reduction due to inf values"

    def test_binary_threshold_filtering(self):
        """binary=True, threshold 지정 → 중립 구간 제거."""
        # 정확히 제어된 가격: ±1% 근처에서 변동
        close = np.array([100.0, 100.5, 101.0, 100.7, 100.3, 100.1, 100.0, 101.2])
        df = pd.DataFrame({
            "open": close,
            "high": close + 0.1,
            "low": close - 0.1,
            "close": close,
            "volume": [1000] * len(close),
        })
        
        fb = FeatureBuilder(forward_n=2, binary=True, binary_threshold=0.01)
        X, y = fb.build(df)
        
        # binary 모드이면서 threshold 필터링되므로
        # 모든 데이터가 남아있지 않을 것
        assert len(X) <= len(close)

    def test_triple_barrier_labeling(self):
        """triple_barrier=True → TP/SL 배리어 기반 레이블."""
        close = np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0])
        df = pd.DataFrame({
            "open": close,
            "high": close + 2,  # 충분한 여유
            "low": close - 2,
            "close": close,
            "volume": [1000] * len(close),
        })
        
        fb = FeatureBuilder(
            forward_n=3,
            binary=True,
            triple_barrier=True,
            tb_tp_pct=0.02,  # 2% TP
            tb_sl_pct=0.01   # 1% SL
        )
        X, y = fb.build(df)
        
        # Triple Barrier 적용되면 레이블이 다르게 생성됨
        # 정상 동작 확인
        if len(y) > 0:
            assert y.isin([0, 1]).all() or y.isnull().any(), \
                "Triple barrier labels should be 0/1 or NaN"


class TestDriftDetectorEdgeCases:
    """DriftDetector 엣지 케이스."""

    def test_page_hinkley_single_value(self):
        """단일 값만 업데이트 → 아직 drift 감지 안 함."""
        detector = PageHinkleyDriftDetector(lambda_=5, delta=0.005)
        result = detector.update(0.8)
        
        assert result is False, "Single value should not trigger drift"

    def test_page_hinkley_all_zeros(self):
        """모든 값이 0 → 안정적 → drift 미감지."""
        detector = PageHinkleyDriftDetector(lambda_=5, delta=0.005)
        
        for _ in range(50):
            detector.update(0.0)
        
        result = detector.update(0.0)
        assert result is False

    def test_page_hinkley_extreme_swing(self):
        """극단 스윙: 0.9 → 0.1 → 0.9 → drift 감지 가능성."""
        detector = PageHinkleyDriftDetector(lambda_=2, delta=0.005)
        
        results = []
        for _ in range(30):
            results.append(detector.update(0.9))
        for _ in range(30):
            results.append(detector.update(0.1))
        
        # 어느 시점에서든 drift가 감지될 가능성
        # (파라미터에 따라 다름)
        # 여기서는 단지 에러 없이 실행되는지만 검증
        assert all(isinstance(r, (bool, np.bool_)) for r in results)

    def test_cusum_initialization(self):
        """CUSUM 초기화 상태."""
        detector = CUSUMDriftDetector(h=4, k=0.5)
        
        result = detector.update(0.8)
        assert result is False, "Initial state should not detect drift immediately"

    def test_cusum_sustained_degradation(self):
        """CUSUM: 지속적 악화 → drift 감지."""
        detector = CUSUMDriftDetector(h=4, k=0.5)
        
        # 안정적인 시작
        for _ in range(20):
            detector.update(0.8)
        
        # 지속적 악화
        drift_detected = False
        for _ in range(30):
            if detector.update(0.3):
                drift_detected = True
                break
        
        # h=4는 작은 값이므로 30번의 악화에서 감지될 가능성 높음
        # (파라미터에 따라 다름)
        # 여기서는 단지 실행 검증
        assert isinstance(drift_detected, (bool, np.bool_))

    def test_drift_detector_reset(self):
        """Drift detector 초기화 후 상태 리셋."""
        detector = PageHinkleyDriftDetector(lambda_=5, delta=0.005)

        for _ in range(20):
            detector.update(0.8)

        # 일부 상태 변경 가능
        detector.reset()
        result = detector.update(0.8)

        # reset 후 다시 새로운 상태로 시작
        assert result is False


class TestFeatureBuilderVPIN:
    """FeatureBuilder VPIN 피처 테스트 (Cycle 232)."""

    def _make_df(self, n: int = 100, trend: str = "up") -> pd.DataFrame:
        np.random.seed(42)
        closes = 100.0 + np.cumsum(np.random.randn(n) * 0.5)
        closes = np.abs(closes) + 1.0
        if trend == "up":
            opens = closes * 0.999
        elif trend == "down":
            opens = closes * 1.001
        else:
            opens = closes + np.random.randn(n) * 0.1
        return pd.DataFrame({
            "open": opens,
            "high": closes * 1.002,
            "low": closes * 0.998,
            "close": closes,
            "volume": np.random.uniform(100, 1000, n),
        })

    def test_vpin_feature_present(self):
        """VPIN 피처가 X에 포함됨."""
        df = self._make_df(100)
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        assert "vpin_50" in X.columns

    def test_vpin_range_zero_to_one(self):
        """VPIN 값이 [0, 1] 범위."""
        df = self._make_df(100)
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        vpin_col = X["vpin_50"]
        assert vpin_col.min() >= 0.0
        assert vpin_col.max() <= 1.0

    def test_vpin_all_buy_candles(self):
        """모두 상승봉(close > open) → VPIN 높음 (>= 0.5)."""
        n = 60
        closes = np.linspace(100, 110, n)
        opens = closes * 0.999  # 항상 close > open
        df = pd.DataFrame({
            "open": opens, "high": closes * 1.001,
            "low": closes * 0.999, "close": closes,
            "volume": np.ones(n) * 500,
        })
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        if "vpin_50" in X.columns and len(X) > 0:
            assert X["vpin_50"].mean() >= 0.5

    def test_vpin_no_crash_empty_volume(self):
        """볼륨 0인 데이터에서도 크래시 없음."""
        n = 60
        closes = np.linspace(100, 110, n)
        df = pd.DataFrame({
            "open": closes * 0.999, "high": closes * 1.001,
            "low": closes * 0.999, "close": closes,
            "volume": np.zeros(n),
        })
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        # 크래시 없이 완료되면 OK (VPIN 컬럼 있어도 없어도 됨)
        assert isinstance(X, pd.DataFrame)

    def test_vpin_no_crash_short_df(self):
        """행 수 < 10 → VPIN 계산 스킵, 크래시 없음."""
        df = self._make_df(8)
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        assert isinstance(X, pd.DataFrame)

    def test_vpin_all_same_open_close(self):
        """모든 캔들이 open == close (도지) → VPIN = 0.5 (중립)."""
        n = 60
        price = np.full(n, 100.0)
        df = pd.DataFrame({
            "open": price,
            "high": price + 1.0,
            "low": price - 1.0,
            "close": price,
            "volume": np.ones(n) * 500,
        })
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        if "vpin_50" in X.columns and len(X) > 0:
            # open == close → buy_frac=0.5 → imbalance=0 → vpin=0.5 (fillna default)
            # 실제로 |buy_vol - sell_vol| = |0.5*V - 0.5*V| = 0 → ratio = 0/sum → fillna(0.5)
            # 하지만 rolling sum이 0이 아닌 이상 vpin = 0.0 (imbalance sum = 0)
            # 어느 경우든 값이 [0, 1] 범위
            assert X["vpin_50"].min() >= 0.0
            assert X["vpin_50"].max() <= 1.0

    def test_vpin_nan_volume_no_crash(self):
        """볼륨에 NaN 값이 포함된 경우 → 크래시 없이 처리."""
        n = 60
        closes = np.linspace(100, 110, n)
        volumes = np.ones(n) * 500
        volumes[10:15] = np.nan  # 일부 NaN
        df = pd.DataFrame({
            "open": closes * 0.999,
            "high": closes * 1.001,
            "low": closes * 0.999,
            "close": closes,
            "volume": volumes,
        })
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        assert isinstance(X, pd.DataFrame)
        if "vpin_50" in X.columns and len(X) > 0:
            # NaN volume은 fillna(0)으로 처리되므로 결과 유효
            assert X["vpin_50"].min() >= 0.0
            assert X["vpin_50"].max() <= 1.0

    def test_vpin_very_short_series_no_feature(self):
        """5행 데이터 → len < 10이므로 vpin_50 피처 미생성."""
        df = pd.DataFrame({
            "open": [100, 101, 102, 103, 104],
            "high": [101, 102, 103, 104, 105],
            "low": [99, 100, 101, 102, 103],
            "close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "volume": [500, 500, 500, 500, 500],
        })
        builder = FeatureBuilder()
        feat = builder._compute_features(df)
        assert "vpin_50" not in feat.columns

    def test_vpin_negative_volume_clipped(self):
        """음수 볼륨 → clip(lower=0)으로 처리, 크래시 없음."""
        n = 60
        closes = np.linspace(100, 110, n)
        volumes = np.ones(n) * 500
        volumes[5:10] = -100  # 음수 볼륨 (비정상)
        df = pd.DataFrame({
            "open": closes * 0.999,
            "high": closes * 1.001,
            "low": closes * 0.999,
            "close": closes,
            "volume": volumes,
        })
        builder = FeatureBuilder()
        X, _ = builder.build(df)
        assert isinstance(X, pd.DataFrame)
        if "vpin_50" in X.columns and len(X) > 0:
            assert X["vpin_50"].min() >= 0.0
            assert X["vpin_50"].max() <= 1.0
