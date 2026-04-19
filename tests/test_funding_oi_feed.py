"""
Tests for Funding Rate + Open Interest data collection and derived features.
Cycle 158: FR delta + OI 파생 피처 추가.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False


# ──────────────────────────────────────────────────────────────────────
# 1. ExchangeConnector FR/OI methods
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not HAS_CCXT, reason="ccxt not installed")
class TestConnectorFundingRate:
    """ExchangeConnector.fetch_funding_rate / fetch_open_interest tests."""

    def _make_connector(self):
        from src.exchange.connector import ExchangeConnector
        conn = ExchangeConnector.__new__(ExchangeConnector)
        conn.exchange_name = "bybit"
        conn.sandbox = True
        conn._exchange = MagicMock()
        conn._consecutive_failures = 0
        conn._max_consecutive_failures = 5
        conn._timeout_ms = 15000
        return conn

    def test_fetch_funding_rate_success(self):
        conn = self._make_connector()
        conn._exchange.fetch_funding_rate.return_value = {
            "fundingRate": 0.0001,
            "timestamp": 1700000000000,
            "symbol": "BTC/USDT:USDT",
        }
        result = conn.fetch_funding_rate("BTC/USDT:USDT")
        assert result["fundingRate"] == 0.0001
        conn._exchange.fetch_funding_rate.assert_called_once()

    def test_fetch_funding_rate_empty_raises(self):
        conn = self._make_connector()
        conn._exchange.fetch_funding_rate.return_value = {}
        # Empty dict is falsy → ValueError raised (no useful data)
        with pytest.raises(ValueError, match="No funding rate"):
            conn.fetch_funding_rate("BTC/USDT:USDT")

    def test_fetch_funding_rate_none_raises(self):
        conn = self._make_connector()
        conn._exchange.fetch_funding_rate.return_value = None
        with pytest.raises(ValueError, match="No funding rate"):
            conn.fetch_funding_rate("BTC/USDT:USDT")

    def test_fetch_funding_rate_history_success(self):
        conn = self._make_connector()
        conn._exchange.fetch_funding_rate_history.return_value = [
            {"fundingRate": 0.0001, "timestamp": 1700000000000},
            {"fundingRate": 0.0002, "timestamp": 1700028800000},
        ]
        result = conn.fetch_funding_rate_history("BTC/USDT:USDT", limit=2)
        assert len(result) == 2
        assert result[0]["fundingRate"] == 0.0001

    def test_fetch_open_interest_success(self):
        conn = self._make_connector()
        conn._exchange.fetch_open_interest.return_value = {
            "openInterestAmount": 12345.67,
            "timestamp": 1700000000000,
            "symbol": "BTC/USDT:USDT",
        }
        result = conn.fetch_open_interest("BTC/USDT:USDT")
        assert result["openInterestAmount"] == 12345.67

    def test_fetch_open_interest_none_raises(self):
        conn = self._make_connector()
        conn._exchange.fetch_open_interest.return_value = None
        with pytest.raises(ValueError, match="No open interest"):
            conn.fetch_open_interest("BTC/USDT:USDT")


# ──────────────────────────────────────────────────────────────────────
# 2. DataFeed FR/OI wrapper methods
# ──────────────────────────────────────────────────────────────────────

class TestDataFeedFundingOI:
    """DataFeed.fetch_funding_rate / fetch_open_interest / compute_fr_oi_features."""

    def _make_feed(self):
        from src.data.feed import DataFeed
        connector = MagicMock()
        return DataFeed(connector)

    def test_fetch_funding_rate_success(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate.return_value = {
            "fundingRate": 0.0003,
            "timestamp": 1700000000000,
        }
        result = feed.fetch_funding_rate("BTC/USDT:USDT")
        assert result == pytest.approx(0.0003)

    def test_fetch_funding_rate_failure_returns_none(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate.side_effect = Exception("API down")
        result = feed.fetch_funding_rate("BTC/USDT:USDT")
        assert result is None

    def test_fetch_funding_rate_missing_key_returns_none(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate.return_value = {"timestamp": 123}
        result = feed.fetch_funding_rate("BTC/USDT:USDT")
        assert result is None

    def test_fetch_open_interest_success(self):
        feed = self._make_feed()
        feed.connector.fetch_open_interest.return_value = {
            "openInterestAmount": 50000.0,
            "timestamp": 1700000000000,
        }
        result = feed.fetch_open_interest("BTC/USDT:USDT")
        assert result == pytest.approx(50000.0)

    def test_fetch_open_interest_failure_returns_none(self):
        feed = self._make_feed()
        feed.connector.fetch_open_interest.side_effect = RuntimeError("fail")
        result = feed.fetch_open_interest("BTC/USDT:USDT")
        assert result is None

    def test_fetch_funding_rate_history_success(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate_history.return_value = [
            {"fundingRate": 0.0001, "timestamp": 1700000000000},
            {"fundingRate": 0.0002, "timestamp": 1700028800000},
            {"fundingRate": -0.0001, "timestamp": 1700057600000},
        ]
        df = feed.fetch_funding_rate_history("BTC/USDT:USDT", limit=3)
        assert len(df) == 3
        assert "funding_rate" in df.columns
        assert df["funding_rate"].iloc[0] == pytest.approx(0.0001)
        assert df["funding_rate"].iloc[2] == pytest.approx(-0.0001)
        # 인덱스가 datetime
        assert pd.api.types.is_datetime64_any_dtype(df.index)

    def test_fetch_funding_rate_history_failure_returns_empty(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate_history.side_effect = Exception("fail")
        df = feed.fetch_funding_rate_history("BTC/USDT:USDT")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert "funding_rate" in df.columns

    def test_fetch_funding_rate_history_empty_records(self):
        feed = self._make_feed()
        feed.connector.fetch_funding_rate_history.return_value = []
        df = feed.fetch_funding_rate_history("BTC/USDT:USDT")
        assert len(df) == 0


# ──────────────────────────────────────────────────────────────────────
# 3. compute_fr_oi_features (static method)
# ──────────────────────────────────────────────────────────────────────

class TestComputeFrOiFeatures:
    """DataFeed.compute_fr_oi_features 파생 피처 계산 검증."""

    def test_basic_computation(self):
        from src.data.feed import DataFeed

        idx = pd.date_range("2024-01-01", periods=5, freq="8h")
        fr = pd.Series([0.0001, 0.0002, -0.0001, 0.0003, 0.0001], index=idx)
        oi = pd.Series([10000, 11000, 10500, 12000, 11500], index=idx)

        result = DataFeed.compute_fr_oi_features(fr, oi)

        assert "funding_rate" in result.columns
        assert "delta_fr" in result.columns
        assert "fr_oi_interaction" in result.columns
        assert len(result) == 5

    def test_delta_fr_values(self):
        from src.data.feed import DataFeed

        idx = pd.date_range("2024-01-01", periods=4, freq="8h")
        fr = pd.Series([0.0001, 0.0003, 0.0002, 0.0005], index=idx)
        oi = pd.Series([10000, 10000, 10000, 10000], index=idx)

        result = DataFeed.compute_fr_oi_features(fr, oi)

        # delta_fr[0] = NaN (diff), delta_fr[1] = 0.0003 - 0.0001 = 0.0002
        assert np.isnan(result["delta_fr"].iloc[0])
        assert result["delta_fr"].iloc[1] == pytest.approx(0.0002)
        assert result["delta_fr"].iloc[2] == pytest.approx(-0.0001)
        assert result["delta_fr"].iloc[3] == pytest.approx(0.0003)

    def test_fr_oi_interaction_normalization(self):
        """OI normalization: oi / rolling_mean(20) → 스케일 보정."""
        from src.data.feed import DataFeed

        idx = pd.date_range("2024-01-01", periods=5, freq="8h")
        fr = pd.Series([0.0001] * 5, index=idx)
        oi = pd.Series([10000] * 5, index=idx)  # 일정한 OI

        result = DataFeed.compute_fr_oi_features(fr, oi)

        # OI가 일정하면 oi_norm ≈ 1.0, interaction ≈ fr
        for i in range(5):
            assert result["fr_oi_interaction"].iloc[i] == pytest.approx(0.0001, abs=1e-8)

    def test_empty_series(self):
        from src.data.feed import DataFeed

        fr = pd.Series([], dtype=float)
        oi = pd.Series([], dtype=float)
        result = DataFeed.compute_fr_oi_features(fr, oi)
        assert len(result) == 0


# ──────────────────────────────────────────────────────────────────────
# 4. FeatureBuilder FR/OI integration
# ──────────────────────────────────────────────────────────────────────

class TestFeatureBuilderFrOi:
    """FeatureBuilder에 funding_rate/open_interest 컬럼이 있을 때 파생 피처 생성 확인."""

    def _make_ohlcv_df(self, n=100):
        """OHLCV + funding_rate + open_interest 포함 DataFrame 생성."""
        np.random.seed(42)
        idx = pd.date_range("2024-01-01", periods=n, freq="1h")
        close = 50000 + np.cumsum(np.random.randn(n) * 100)
        high = close + np.abs(np.random.randn(n) * 50)
        low = close - np.abs(np.random.randn(n) * 50)
        open_ = close + np.random.randn(n) * 30
        volume = np.random.uniform(100, 1000, n)

        df = pd.DataFrame({
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }, index=idx)
        return df

    def test_no_fr_columns_baseline(self):
        """funding_rate 컬럼 없을 때 기존 피처만 생성."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df()
        X, y = fb.build(df)

        assert "delta_fr" not in X.columns
        assert "fr_oi_interaction" not in X.columns

    def test_with_funding_rate_only(self):
        """funding_rate 컬럼만 있을 때 delta_fr 생성, fr_oi_interaction 미생성."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df()
        df["funding_rate"] = np.random.uniform(-0.001, 0.001, len(df))

        X, y = fb.build(df)

        assert "delta_fr" in X.columns
        assert "fr_oi_interaction" not in X.columns

    def test_with_both_fr_and_oi(self):
        """funding_rate + open_interest 둘 다 있을 때 delta_fr, fr_oi_interaction 생성."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df()
        df["funding_rate"] = np.random.uniform(-0.001, 0.001, len(df))
        df["open_interest"] = np.random.uniform(5000, 15000, len(df))

        X, y = fb.build(df)

        assert "delta_fr" in X.columns
        assert "fr_oi_interaction" in X.columns
        # delta_fr: diff이므로 첫 행 NaN → dropna 후 제거됨
        assert not X["delta_fr"].isna().any()

    def test_feature_count_with_fr_oi(self):
        """base 14 + delta_fr + fr_oi_interaction = 16 피처."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df()
        df["funding_rate"] = np.random.uniform(-0.001, 0.001, len(df))
        df["open_interest"] = np.random.uniform(5000, 15000, len(df))

        X, y = fb.build(df)

        # base 14 + delta_fr + fr_oi_interaction = 16
        assert len(X.columns) == 16

    def test_delta_fr_correctness(self):
        """delta_fr = fr[t] - fr[t-1] 정확성 검증."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df(n=50)
        fr_vals = [0.0001 * i for i in range(50)]
        df["funding_rate"] = fr_vals

        feat = fb._compute_features(df)

        # delta_fr[1] = 0.0001*1 - 0.0001*0 = 0.0001
        assert feat["delta_fr"].iloc[1] == pytest.approx(0.0001, abs=1e-8)
        # delta_fr[2] = 0.0001*2 - 0.0001*1 = 0.0001
        assert feat["delta_fr"].iloc[2] == pytest.approx(0.0001, abs=1e-8)

    def test_no_inf_values(self):
        """FR/OI 피처에 inf 값이 없어야 함."""
        from src.ml.features import FeatureBuilder

        fb = FeatureBuilder()
        df = self._make_ohlcv_df()
        df["funding_rate"] = np.random.uniform(-0.001, 0.001, len(df))
        df["open_interest"] = np.random.uniform(5000, 15000, len(df))

        feat = fb._compute_features(df)

        assert not np.isinf(feat["delta_fr"]).any()
        assert not np.isinf(feat["fr_oi_interaction"]).any()
