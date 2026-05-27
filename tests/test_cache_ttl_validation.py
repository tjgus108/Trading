"""
Tests for DataFeed cache TTL consistency validation (Cycle 231).
"""

import unittest
from unittest.mock import Mock, patch
from src.data.feed import DataFeed


class TestCacheTTLConfig(unittest.TestCase):
    def setUp(self):
        """Create mock ExchangeConnector for DataFeed."""
        self.mock_connector = Mock()
        self.mock_connector.health_check.return_value = {"connected": True}
        self.feed = DataFeed(self.mock_connector, cache_ttl=60)
    
    def test_get_ttl_config_returns_all_settings(self):
        """get_ttl_config should return all cache TTL settings."""
        config = self.feed.get_ttl_config()
        
        self.assertIn('ohlcv_base_ttl', config)
        self.assertIn('order_book_ttl', config)
        self.assertIn('regime_cache_ttl', config)
        self.assertIn('stale_reuse_ttl', config)
        self.assertIn('regime_ttl_multipliers', config)
        self.assertIn('effective_ttl_formula', config)
    
    def test_ttl_config_ohlcv_base(self):
        """OHLCV base TTL should match constructor."""
        config = self.feed.get_ttl_config()
        self.assertEqual(config['ohlcv_base_ttl'], 60)
    
    def test_ttl_config_order_book(self):
        """Order book TTL should be 5 seconds (short for real-time updates)."""
        config = self.feed.get_ttl_config()
        self.assertEqual(config['order_book_ttl'], 5)
    
    def test_ttl_config_regime_multipliers(self):
        """Regime multipliers should be defined."""
        config = self.feed.get_ttl_config()
        multipliers = config['regime_ttl_multipliers']
        
        self.assertIn('high_volatility', multipliers)
        self.assertIn('crisis', multipliers)
        self.assertIn('low_volatility', multipliers)
        self.assertIn('trending', multipliers)
    
    def test_regime_multiplier_values(self):
        """Regime multipliers should have reasonable values."""
        config = self.feed.get_ttl_config()
        multipliers = config['regime_ttl_multipliers']
        
        # Crisis should be shortest TTL
        self.assertLess(multipliers['crisis'], multipliers['high_volatility'])
        
        # Low volatility should be longer than base
        self.assertGreater(multipliers['low_volatility'], 1.0)
        
        # All multipliers should be positive
        for mult in multipliers.values():
            self.assertGreater(mult, 0.0)


class TestCacheTTLConsistency(unittest.TestCase):
    def setUp(self):
        """Create mock ExchangeConnector for DataFeed."""
        self.mock_connector = Mock()
        self.mock_connector.health_check.return_value = {"connected": True}
        self.feed = DataFeed(self.mock_connector, cache_ttl=60)
    
    def test_ttl_consistency_returns_dict(self):
        """validate_ttl_consistency should return a dict with expected keys."""
        result = self.feed.validate_ttl_consistency()
        
        self.assertIn('is_consistent', result)
        self.assertIn('issues', result)
        self.assertIn('warnings', result)
        self.assertIn('cache_sizes', result)
        self.assertIn('ttl_ranges', result)
    
    def test_default_ttl_is_consistent(self):
        """Default TTL settings should be consistent."""
        result = self.feed.validate_ttl_consistency()
        
        # Default settings should not have critical issues
        self.assertTrue(result['is_consistent'], 
                       f"Inconsistencies found: {result['issues']}")
    
    def test_cache_sizes_reported(self):
        """Cache sizes should be reported."""
        result = self.feed.validate_ttl_consistency()
        sizes = result['cache_sizes']
        
        self.assertIn('ohlcv', sizes)
        self.assertIn('order_book', sizes)
        self.assertIn('regime', sizes)
        
        # All sizes should be non-negative
        for size in sizes.values():
            self.assertGreaterEqual(size, 0)
    
    def test_ttl_ranges_calculated(self):
        """TTL ranges should be calculated."""
        result = self.feed.validate_ttl_consistency()
        ranges = result['ttl_ranges']
        
        self.assertIn('min_ttl', ranges)
        self.assertIn('max_ttl', ranges)
        self.assertIn('mean_ttl', ranges)
        
        # min should be <= max
        self.assertLessEqual(ranges['min_ttl'], ranges['max_ttl'])
        
        # mean should be in range
        self.assertGreaterEqual(ranges['mean_ttl'], ranges['min_ttl'])
        self.assertLessEqual(ranges['mean_ttl'], ranges['max_ttl'])
    
    def test_order_book_ttl_shorter_than_ohlcv(self):
        """Order book TTL (5s) should be shorter than OHLCV (60s)."""
        result = self.feed.validate_ttl_consistency()
        
        # No critical issue about this
        issues_str = " ".join(result['issues'])
        self.assertNotIn("Order book TTL", issues_str,
                        "Order book TTL should be shorter than OHLCV")
    
    def test_regime_multipliers_valid(self):
        """All regime multipliers should be positive."""
        result = self.feed.validate_ttl_consistency()
        
        # No issues about invalid multipliers
        issues_str = " ".join(result['issues'])
        self.assertNotIn("Invalid regime multiplier", issues_str)


class TestCacheTTLDocumentation(unittest.TestCase):
    """Verify cache TTL is documented consistently."""
    
    def test_readme_or_docs_exist(self):
        """Cache TTL documentation should be available."""
        # This test verifies the get_ttl_config method exists and returns proper docs
        mock_connector = Mock()
        mock_connector.health_check.return_value = {"connected": True}
        feed = DataFeed(mock_connector, cache_ttl=60)
        
        config = feed.get_ttl_config()
        self.assertIn('effective_ttl_formula', config)
        # Verify the formula is documented
        self.assertTrue(len(config['effective_ttl_formula']) > 0)


if __name__ == '__main__':
    unittest.main()
