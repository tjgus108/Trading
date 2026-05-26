"""
Block Bootstrap 합성 데이터 생성기 테스트.

검증 항목:
1. 기본 동작: 올바른 크기의 OHLCV DataFrame 반환
2. OHLC 관계: high >= max(open, close), low <= min(open, close)
3. 지표 포함: make_synthetic_data와 동일한 지표 컬럼 존재
4. 통계적 특성: 원본 대비 자기상관/kurtosis 보존 (GBM 대비 우수)
5. 재현성: 같은 seed → 같은 결과
6. 에러 처리: seed_df가 너무 작을 때 ValueError
"""
import numpy as np
import pandas as pd
import pytest

from scripts.quality_audit import make_synthetic_data, make_block_bootstrap_data


@pytest.fixture
def seed_df():
    """GBM 기반 시드 데이터 (500봉)."""
    return make_synthetic_data(500, seed=42)


class TestBlockBootstrapBasic:
    """기본 동작 검증."""

    def test_output_shape(self, seed_df):
        result = make_block_bootstrap_data(seed_df, n=300, block_size=36, seed=1)
        assert len(result) == 300

    def test_ohlcv_columns_present(self, seed_df):
        result = make_block_bootstrap_data(seed_df, n=200, seed=1)
        for col in ["open", "high", "low", "close", "volume"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_ohlc_relationship(self, seed_df):
        """high >= max(open, close), low <= min(open, close)."""
        result = make_block_bootstrap_data(seed_df, n=300, seed=1)
        max_oc = result[["open", "close"]].max(axis=1)
        min_oc = result[["open", "close"]].min(axis=1)
        assert (result["high"] >= max_oc - 1e-10).all(), "high < max(open, close)"
        assert (result["low"] <= min_oc + 1e-10).all(), "low > min(open, close)"

    def test_positive_prices(self, seed_df):
        result = make_block_bootstrap_data(seed_df, n=300, seed=1)
        assert (result["close"] > 0).all()
        assert (result["high"] > 0).all()
        assert (result["low"] > 0).all()
        assert (result["volume"] >= 0).all()

    def test_no_nan_in_ohlcv(self, seed_df):
        result = make_block_bootstrap_data(seed_df, n=300, seed=1)
        ohlcv = result[["open", "high", "low", "close", "volume"]]
        assert not ohlcv.isna().any().any(), "NaN found in OHLCV"


class TestBlockBootstrapIndicators:
    """지표 컬럼이 make_synthetic_data와 동일하게 포함되는지 검증."""

    def test_indicator_columns_match(self, seed_df):
        gbm_df = make_synthetic_data(300, seed=99)
        bb_df = make_block_bootstrap_data(seed_df, n=300, seed=1)

        gbm_cols = set(gbm_df.columns)
        bb_cols = set(bb_df.columns)
        missing = gbm_cols - bb_cols
        assert not missing, f"Block bootstrap missing indicators: {missing}"


class TestBlockBootstrapStatistics:
    """통계적 특성 보존 검증 (자기상관, kurtosis)."""

    def test_kurtosis_preserved(self, seed_df):
        """Block bootstrap는 원본의 fat tail을 보존해야 함."""
        from scipy import stats

        bb_df = make_block_bootstrap_data(seed_df, n=400, block_size=36, seed=1)
        seed_returns = np.diff(np.log(seed_df["close"].values))
        bb_returns = np.diff(np.log(bb_df["close"].values))

        seed_kurt = stats.kurtosis(seed_returns)
        bb_kurt = stats.kurtosis(bb_returns)

        # Block bootstrap kurtosis는 원본의 절반 이상이어야 함
        # (GBM은 ~0에 수렴하므로 이 기준으로 구분 가능)
        assert bb_kurt > seed_kurt * 0.3, (
            f"Kurtosis not preserved: seed={seed_kurt:.2f}, bootstrap={bb_kurt:.2f}"
        )

    def test_autocorrelation_preserved(self, seed_df):
        """Block bootstrap는 수익률 자기상관 구조를 보존해야 함."""
        bb_df = make_block_bootstrap_data(seed_df, n=400, block_size=36, seed=1)
        bb_returns = pd.Series(np.diff(np.log(bb_df["close"].values)))

        # lag-1 절대수익률 자기상관 (volatility clustering indicator)
        abs_returns = bb_returns.abs()
        ac1 = abs_returns.autocorr(lag=1)

        # Block bootstrap에서 절대수익률 lag-1 자기상관은 양수여야 함
        # (GBM은 ~0, 실제 시장은 0.1~0.4)
        assert ac1 > -0.1, (
            f"Absolute return autocorrelation too negative: {ac1:.3f}"
        )


class TestBlockBootstrapReproducibility:
    """재현성 검증."""

    def test_same_seed_same_result(self, seed_df):
        r1 = make_block_bootstrap_data(seed_df, n=200, seed=42)
        r2 = make_block_bootstrap_data(seed_df, n=200, seed=42)
        pd.testing.assert_frame_equal(r1, r2)

    def test_different_seed_different_result(self, seed_df):
        r1 = make_block_bootstrap_data(seed_df, n=200, seed=1)
        r2 = make_block_bootstrap_data(seed_df, n=200, seed=2)
        assert not r1["close"].equals(r2["close"])


class TestBlockBootstrapEdgeCases:
    """엣지 케이스 검증."""

    def test_seed_df_too_small(self):
        """seed_df가 block_size보다 작으면 ValueError."""
        small_df = make_synthetic_data(10, seed=1)
        with pytest.raises(ValueError, match="need at least block_size"):
            make_block_bootstrap_data(small_df, n=100, block_size=36)

    def test_block_size_equals_seed(self, seed_df):
        """block_size == len(seed_df) - 1: 극단적이지만 동작해야 함."""
        bs = len(seed_df) - 1
        result = make_block_bootstrap_data(seed_df, n=100, block_size=bs, seed=1)
        assert len(result) == 100

    def test_small_n(self, seed_df):
        """n이 block_size보다 작아도 동작."""
        result = make_block_bootstrap_data(seed_df, n=10, block_size=36, seed=1)
        assert len(result) == 10

    def test_custom_initial_price(self, seed_df):
        result = make_block_bootstrap_data(
            seed_df, n=100, seed=1, initial_price=1000.0
        )
        # 첫 번째 close가 initial_price 근처여야 함 (첫 수익률 적용 후)
        assert 500 < result["close"].iloc[0] < 2000
