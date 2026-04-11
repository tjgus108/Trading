"""
DataFeed.fetch_multiple() 병렬 fetch 테스트.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.data.feed import DataFeed, DataSummary


class TestFeedParallel:
    """병렬 fetch 기능 테스트."""

    def test_fetch_multiple_basic(self):
        """여러 심볼 병렬 fetch."""
        # Mock connector
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            # BTC/USDT
            [[1704067200000, 42000, 42500, 41800, 42300, 100]],
            # ETH/USDT
            [[1704067200000, 2500, 2600, 2450, 2550, 500]],
        ]

        feed = DataFeed(connector)
        
        symbols = ["BTC/USDT", "ETH/USDT"]
        results = feed.fetch_multiple(symbols, "1h", limit=500)

        # 결과 검증
        assert len(results) == 2
        assert "BTC/USDT" in results
        assert "ETH/USDT" in results
        
        btc_summary = results["BTC/USDT"]
        eth_summary = results["ETH/USDT"]
        
        assert isinstance(btc_summary, DataSummary)
        assert isinstance(eth_summary, DataSummary)
        assert btc_summary.symbol == "BTC/USDT"
        assert eth_summary.symbol == "ETH/USDT"
        assert btc_summary.candles == 1
        assert eth_summary.candles == 1

    def test_fetch_multiple_caching(self):
        """병렬 fetch도 캐싱 동작."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]

        feed = DataFeed(connector, cache_ttl=60)
        
        symbols = ["BTC/USDT", "ETH/USDT"]
        
        # 첫 번째 호출
        results1 = feed.fetch_multiple(symbols, "1h", limit=500)
        # 두 번째 호출
        results2 = feed.fetch_multiple(symbols, "1h", limit=500)

        # 캐시 덕분에 fetch_ohlcv는 2번만 호출 (각 심볼당 1회)
        # 캐시된 데이터는 재사용
        assert connector.fetch_ohlcv.call_count == 2

    def test_fetch_multiple_partial_failure(self):
        """일부 심볼 실패 시 다른 심볼은 계속 처리."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            Exception("API error"),  # BTC 실패
            [[1704067200000, 2500, 2600, 2450, 2550, 500]],  # ETH 성공
        ]

        feed = DataFeed(connector)
        
        symbols = ["BTC/USDT", "ETH/USDT"]
        results = feed.fetch_multiple(symbols, "1h", limit=500)

        # ETH만 성공
        assert "ETH/USDT" in results
        assert results["ETH/USDT"].symbol == "ETH/USDT"
        assert "BTC/USDT" not in results

    def test_fetch_multiple_empty_symbols(self):
        """빈 심볼 리스트."""
        connector = MagicMock()
        feed = DataFeed(connector)
        
        results = feed.fetch_multiple([], "1h", limit=500)
        assert results == {}

    def test_fetch_multiple_max_workers(self):
        """max_workers 지정."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]

        feed = DataFeed(connector)
        
        symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT"]
        # max_workers=2 지정
        results = feed.fetch_multiple(
            symbols, "1h", limit=500, max_workers=2
        )

        assert len(results) == 3
        assert connector.fetch_ohlcv.call_count == 3

    def test_fetch_multiple_single_symbol(self):
        """단일 심볼도 처리 가능."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]

        feed = DataFeed(connector)
        
        results = feed.fetch_multiple(["BTC/USDT"], "1h", limit=500)
        assert len(results) == 1
        assert "BTC/USDT" in results

    def test_fetch_multiple_indicators_included(self):
        """병렬 fetch된 데이터도 지표 포함."""
        connector = MagicMock()
        # 충분한 데이터로 지표 계산
        raw_data = [
            [1704067200000 + i*3600000, 42000+i*10, 42500+i*10, 41800+i*10, 42300+i*10, 100]
            for i in range(50)
        ]
        connector.fetch_ohlcv.return_value = raw_data

        feed = DataFeed(connector)
        results = feed.fetch_multiple(["BTC/USDT"], "1h", limit=500)

        btc_summary = results["BTC/USDT"]
        
        # 지표 확인
        assert "ema20" in btc_summary.indicators
        assert "ema50" in btc_summary.indicators
        assert "atr14" in btc_summary.indicators
        assert "rsi14" in btc_summary.indicators
        assert "donchian_high" in btc_summary.indicators
        assert "vwap" in btc_summary.indicators


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
