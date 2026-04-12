"""
OHLC 관계 검증 테스트
"""

from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.data.feed import DataFeed


class TestOHLCValidation:
    """OHLC 관계 검증 테스트."""

    def test_valid_ohlc_relationships(self):
        """정상 OHLC 데이터: 이상 감지 없음."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42200, 100],  # high=42500 >= max(42000,42200), low=41800 <= min(42000,42200)
            [1704070800000, 42200, 42800, 42000, 42500, 150],  # 정상
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 OHLC 관련 이상이 없어야 함
        ohlc_issues = [a for a in result.anomalies if 'high' in a or 'low' in a]
        assert len(ohlc_issues) == 0, f"정상 데이터인데 이상 감지: {ohlc_issues}"

    def test_high_less_than_max_open_close(self):
        """high < max(open, close) 감지."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 41500, 41800, 42200, 100],  # high=41500 < max(42000,42200)=42200 (오류!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 high 이상 감지
        assert any('high < max(open,close)' in a for a in result.anomalies), \
            f"high 이상 미감지: {result.anomalies}"

    def test_low_greater_than_min_open_close(self):
        """low > min(open, close) 감지."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 42100, 42200, 100],  # low=42100 > min(42000,42200)=42000 (오류!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 low 이상 감지
        assert any('low > min(open,close)' in a for a in result.anomalies), \
            f"low 이상 미감지: {result.anomalies}"

    def test_high_less_than_low(self):
        """high < low 감지 (기존 로직)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 41500, 42200, 42100, 100],  # high=41500 < low=42200 (역전!)
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # anomalies에 역전 감지
        assert any('high < low' in a for a in result.anomalies), \
            f"역전 미감지: {result.anomalies}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
