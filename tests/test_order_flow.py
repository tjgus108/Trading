"""
Tests for src/data/order_flow.py
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from src.data.order_flow import OrderFlowFetcher, OrderFlowData, _ofi_to_score, _pressure_from_ofi


class TestOfiToScore(unittest.TestCase):
    def test_ofi_zero_gives_zero_score(self):
        self.assertAlmostEqual(_ofi_to_score(0.0), 0.0)

    def test_ofi_one_gives_max_score(self):
        self.assertAlmostEqual(_ofi_to_score(1.0), 3.0)

    def test_ofi_minus_one_gives_min_score(self):
        self.assertAlmostEqual(_ofi_to_score(-1.0), -3.0)

    def test_score_clamp_upper(self):
        self.assertEqual(_ofi_to_score(2.0), 3.0)

    def test_score_clamp_lower(self):
        self.assertEqual(_ofi_to_score(-2.0), -3.0)


class TestPressureFromOfi(unittest.TestCase):
    def test_neutral_boundary(self):
        self.assertEqual(_pressure_from_ofi(0.0), "NEUTRAL")
        self.assertEqual(_pressure_from_ofi(0.3), "NEUTRAL")
        self.assertEqual(_pressure_from_ofi(-0.3), "NEUTRAL")

    def test_buy_pressure(self):
        self.assertEqual(_pressure_from_ofi(0.31), "BUY_PRESSURE")
        self.assertEqual(_pressure_from_ofi(1.0), "BUY_PRESSURE")

    def test_sell_pressure(self):
        self.assertEqual(_pressure_from_ofi(-0.31), "SELL_PRESSURE")
        self.assertEqual(_pressure_from_ofi(-1.0), "SELL_PRESSURE")


class TestMockMethod(unittest.TestCase):
    def setUp(self):
        self.fetcher = OrderFlowFetcher()

    def test_mock_neutral(self):
        """score == 0 when ofi=0.0"""
        result = self.fetcher.mock(ofi=0.0)
        self.assertIsInstance(result, OrderFlowData)
        self.assertEqual(result.score, 0.0)
        self.assertEqual(result.pressure, "NEUTRAL")
        self.assertEqual(result.source, "mock")

    def test_buy_pressure_positive_score(self):
        """ofi=0.5 → score > 0"""
        result = self.fetcher.mock(ofi=0.5)
        self.assertGreater(result.score, 0)
        self.assertEqual(result.pressure, "BUY_PRESSURE")

    def test_sell_pressure_negative_score(self):
        """ofi=-0.5 → score < 0"""
        result = self.fetcher.mock(ofi=-0.5)
        self.assertLess(result.score, 0)
        self.assertEqual(result.pressure, "SELL_PRESSURE")

    def test_score_bounded_positive(self):
        """score always in [-3, 3]"""
        result = self.fetcher.mock(ofi=0.9)
        self.assertGreaterEqual(result.score, -3.0)
        self.assertLessEqual(result.score, 3.0)

    def test_score_bounded_negative(self):
        result = self.fetcher.mock(ofi=-0.9)
        self.assertGreaterEqual(result.score, -3.0)
        self.assertLessEqual(result.score, 3.0)

    def test_mock_ofi_clamped(self):
        """ofi values outside [-1,1] are clamped"""
        result = self.fetcher.mock(ofi=5.0)
        self.assertLessEqual(result.score, 3.0)
        result2 = self.fetcher.mock(ofi=-5.0)
        self.assertGreaterEqual(result2.score, -3.0)

    def test_mock_returns_dataclass(self):
        result = self.fetcher.mock(ofi=0.2)
        self.assertIsInstance(result, OrderFlowData)
        self.assertIn(result.pressure, ["BUY_PRESSURE", "SELL_PRESSURE", "NEUTRAL"])


class TestFetchFailure(unittest.TestCase):
    def test_fetch_failure_returns_zero(self):
        """Network failure → score=0, source='unavailable'"""
        fetcher = OrderFlowFetcher()
        with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
            result = fetcher.fetch()
        self.assertEqual(result.score, 0.0)
        self.assertEqual(result.source, "unavailable")
        self.assertEqual(result.ofi, 0.0)

    def test_fetch_success_parses_orderbook(self):
        """Successful fetch returns valid OrderFlowData"""
        fake_response = json.dumps({
            "bids": [["50000", "1.0"], ["49999", "2.0"]],
            "asks": [["50001", "0.5"], ["50002", "0.5"]],
        }).encode()

        fetcher = OrderFlowFetcher()
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_response
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = fetcher.fetch()

        # bid_vol=3.0, ask_vol=1.0, ofi=(3-1)/4=0.5
        self.assertAlmostEqual(result.ofi, 0.5)
        self.assertGreater(result.score, 0)
        self.assertEqual(result.source, "binance")

    def test_fetch_uses_cache(self):
        """Second call within cache window returns cached result without network"""
        fake_response = json.dumps({
            "bids": [["50000", "1.0"]],
            "asks": [["50001", "1.0"]],
        }).encode()

        fetcher = OrderFlowFetcher(use_cache_seconds=60)
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_response
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_url:
            fetcher.fetch()
            fetcher.fetch()  # second call — should use cache
            self.assertEqual(mock_url.call_count, 1)


if __name__ == "__main__":
    unittest.main()
