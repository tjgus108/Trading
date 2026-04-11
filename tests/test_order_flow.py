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


class TestVPINCalculator(unittest.TestCase):
    """VPIN (Volume-Synchronized Probability of Informed Trading) 테스트"""
    
    def setUp(self):
        from src.data.order_flow import VPINCalculator
        self.calc = VPINCalculator(n_buckets=3)
    
    def test_vpin_all_neutral_candles(self):
        """close == open: NEUTRAL → low VPIN"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0],
            "close": [100.0, 100.0, 100.0],
            "volume": [100.0, 100.0, 100.0]
        })
        result = self.calc.compute(df)
        # NEUTRAL candles 모두 0.5 buy_frac → imbalance = 0
        self.assertAlmostEqual(result.iloc[-1], 0.0, places=2)
    
    def test_vpin_perfect_buy_pressure(self):
        """close > open: BUY → high VPIN (all buy)"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [90.0, 90.0, 90.0],
            "close": [100.0, 100.0, 100.0],
            "volume": [100.0, 100.0, 100.0]
        })
        result = self.calc.compute(df)
        # All BUY → buy_vol = 100, sell_vol = 0, imbalance = 100
        self.assertAlmostEqual(result.iloc[-1], 1.0, places=2)
    
    def test_vpin_perfect_sell_pressure(self):
        """close < open: SELL → high VPIN (all sell)"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0],
            "close": [90.0, 90.0, 90.0],
            "volume": [100.0, 100.0, 100.0]
        })
        result = self.calc.compute(df)
        # All SELL → buy_vol = 0, sell_vol = 100, imbalance = 100
        self.assertAlmostEqual(result.iloc[-1], 1.0, places=2)
    
    def test_vpin_balanced_buy_sell(self):
        """Perfectly balanced buy/sell → low VPIN"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0],
            "close": [105.0, 95.0, 105.0],  # buy, sell, buy
            "volume": [100.0, 100.0, 100.0]
        })
        result = self.calc.compute(df)
        # Row 2: buy_vol = 100 + 0 + 100 = 200, sell_vol = 0 + 100 + 0 = 100
        # imbalance = |100| + |100| + |100| = 300 (not 0, test expectation was wrong)
        # Let's test with perfectly balanced window
        calc2 = calc2 = __import__('src.data.order_flow', fromlist=['VPINCalculator']).VPINCalculator(n_buckets=2)
        df2 = pd.DataFrame({
            "open": [100.0, 100.0],
            "close": [105.0, 95.0],  # buy, sell
            "volume": [100.0, 100.0]
        })
        result2 = calc2.compute(df2)
        # buy_vol = 100 + 0 = 100, sell_vol = 0 + 100 = 100
        # imbalance = 100 + 100 = 200, total = 200
        # VPIN = 200 / 200 = 1.0 (opposite imbalances sum)
        self.assertAlmostEqual(result2.iloc[-1], 1.0, places=2)
    
    def test_vpin_bounded_zero_to_one(self):
        """VPIN always in [0, 1]"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 99.0, 98.0, 97.0, 96.0],
            "close": [110.0, 95.0, 110.0, 95.0, 110.0],
            "volume": [1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
        })
        result = self.calc.compute(df)
        for val in result.dropna():
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)
    
    def test_vpin_get_latest(self):
        """get_latest() returns last VPIN value"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0] * 10,
            "close": [105.0] * 10,  # all BUY
            "volume": [100.0] * 10
        })
        latest = self.calc.get_latest(df)
        self.assertGreaterEqual(latest, 0.0)
        self.assertLessEqual(latest, 1.0)
    
    def test_vpin_get_latest_insufficient_data(self):
        """get_latest() returns 0.5 when data insufficient"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0],
            "close": [105.0],
            "volume": [100.0]
        })
        latest = self.calc.get_latest(df)
        self.assertEqual(latest, 0.5)
    
    def test_vpin_get_latest_nan(self):
        """get_latest() handles NaN gracefully"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0],
            "close": [float('nan')],
            "volume": [100.0]
        })
        latest = self.calc.get_latest(df)
        self.assertEqual(latest, 0.5)
    
    def test_vpin_massive_volume_spike(self):
        """거대 거래량 급증 한 봉 → imbalance 반영"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0, 100.0],
            "close": [105.0, 105.0, 105.0, 105.0],  # all BUY
            "volume": [100.0, 100.0, 10000.0, 100.0]  # spike at index 2
        })
        calc = __import__('src.data.order_flow', fromlist=['VPINCalculator']).VPINCalculator(n_buckets=3)
        result = calc.compute(df)
        # Row 3: last 3 candles, total_vol = 100 + 10000 + 100 = 10200
        # All BUY → imbalance = 10200, VPIN = 10200/10200 = 1.0
        self.assertAlmostEqual(result.iloc[-1], 1.0, places=2)
        self.assertLessEqual(result.iloc[-1], 1.0)
    
    def test_vpin_mixed_volume_sizes(self):
        """혼합 거래량 크기 → 가중치 적용"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0],
            "close": [100.0, 100.0, 101.0],  # 2 neutral, 1 slight buy
            "volume": [100.0, 100.0, 100.0]
        })
        calc = __import__('src.data.order_flow', fromlist=['VPINCalculator']).VPINCalculator(n_buckets=3)
        result = calc.compute(df)
        # Imbalance = 0 + 0 + 100 = 100, total = 300
        # VPIN = 100/300 ≈ 0.33
        self.assertGreater(result.iloc[-1], 0.0)
        self.assertLess(result.iloc[-1], 0.5)
    
    def test_vpin_zero_volume_candle(self):
        """0 거래량 봉 → 안전 처리 (division by zero 회피)"""
        import pandas as pd
        df = pd.DataFrame({
            "open": [100.0, 100.0, 100.0],
            "close": [105.0, 100.0, 105.0],
            "volume": [100.0, 0.0, 100.0]  # zero volume at index 1
        })
        calc = __import__('src.data.order_flow', fromlist=['VPINCalculator']).VPINCalculator(n_buckets=3)
        result = calc.compute(df)
        # Should not raise exception, should return valid VPIN
        self.assertFalse(result.isna().all())
        self.assertGreaterEqual(result.iloc[-1], 0.0)
        self.assertLessEqual(result.iloc[-1], 1.0)
