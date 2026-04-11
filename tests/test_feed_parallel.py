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

    def test_fetch_with_retry_logging(self):
        """Fetch retry 시 에러 로그에 symbol, timeframe, attempt 정보 포함."""
        connector = MagicMock()
        # 처음 2번 실패, 3번째 성공
        connector.fetch_ohlcv.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            [[1704067200000, 42000, 42500, 41800, 42300, 100]],
        ]

        feed = DataFeed(connector, max_retries=3)
        
        with patch("src.data.feed.logger") as mock_logger:
            result = feed.fetch("BTC/USDT", "1h", limit=500)
            
            assert result.symbol == "BTC/USDT"
            # Warning 로그 확인 (시도 1, 2에서)
            warning_calls = mock_logger.warning.call_args_list
            assert len(warning_calls) == 2
            # call('format', 'BTC/USDT', '1h', error_msg, 1, 3)
            call_args_0 = warning_calls[0][0]
            call_args_1 = warning_calls[1][0]
            
            # 첫 번째 warning: attempt 1/3
            assert "BTC/USDT" in call_args_0[1]
            assert "1h" in call_args_0[2]
            assert call_args_0[4] == 1  # attempt
            assert call_args_0[5] == 3  # max_retries
            
            # 두 번째 warning: attempt 2/3
            assert "BTC/USDT" in call_args_1[1]
            assert "1h" in call_args_1[2]
            assert call_args_1[4] == 2  # attempt
            assert call_args_1[5] == 3  # max_retries

    def test_fetch_max_retries_exceeded(self):
        """모든 retry 실패 후 에러 로그 + 예외 발생."""
        connector = MagicMock()
        error = Exception("Persistent API error")
        connector.fetch_ohlcv.side_effect = error

        feed = DataFeed(connector, max_retries=2)
        
        with patch("src.data.feed.logger") as mock_logger:
            with pytest.raises(Exception) as exc_info:
                feed.fetch("ETH/USDT", "4h", limit=100)
            
            assert str(exc_info.value) == "Persistent API error"
            # Error 로그 확인 — 개선된 포맷 확인
            error_calls = mock_logger.error.call_args_list
            assert len(error_calls) >= 1
            error_call_args = error_calls[0][0]
            # 새 포맷: symbol, timeframe, limit, max_retries, error_type, message
            assert error_call_args[1] == "ETH/USDT"  # symbol
            assert error_call_args[2] == "4h"  # timeframe
            assert error_call_args[3] == 100  # limit
            assert error_call_args[4] == 2  # max_retries

    def test_fetch_error_log_includes_context(self):
        """Fetch 실패 시 에러 로그에 symbol, timeframe, limit, max_retries, error_type 포함."""
        connector = MagicMock()
        error = ValueError("Invalid data format")
        connector.fetch_ohlcv.side_effect = error

        feed = DataFeed(connector, max_retries=3)
        
        with patch("src.data.feed.logger") as mock_logger:
            with pytest.raises(ValueError):
                feed.fetch("BTC/USDT", "1h", limit=500)
            
            # Error 로그 확인
            error_calls = mock_logger.error.call_args_list
            assert len(error_calls) >= 1
            
            error_call = error_calls[0]
            # 호출의 format string은 [0][0][0], 인자들은 [0][0][1:]
            call_args = error_call[0]  # (format_string, arg1, arg2, ...)
            
            # 포맷 문자열 확인
            format_str = call_args[0]
            assert "symbol=%s" in format_str
            assert "timeframe=%s" in format_str
            assert "limit=%d" in format_str
            assert "max_retries=%d" in format_str
            assert "error_type=%s" in format_str
            assert "message=%s" in format_str
            
            # 인자 확인
            assert call_args[1] == "BTC/USDT"  # symbol
            assert call_args[2] == "1h"  # timeframe
            assert call_args[3] == 500  # limit
            assert call_args[4] == 3  # max_retries
            assert call_args[5] == "ValueError"  # error_type
            assert "Invalid data format" in call_args[6]  # message
    def test_cache_stats_initial(self):
        """캐시 통계 초기값 (hit=0, miss=0)."""
        connector = MagicMock()
        feed = DataFeed(connector)
        
        stats = feed.cache_stats()
        
        assert stats['hit_count'] == 0
        assert stats['miss_count'] == 0
        assert stats['total'] == 0
        assert stats['hit_rate'] == 0.0
        assert stats['cached_keys'] == 0

    def test_cache_stats_after_fetch(self):
        """첫 fetch 후 miss=1, hit=0."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector)
        feed.fetch("BTC/USDT", "1h", limit=500)
        
        stats = feed.cache_stats()
        
        assert stats['hit_count'] == 0
        assert stats['miss_count'] == 1
        assert stats['total'] == 1
        assert stats['hit_rate'] == 0.0
        assert stats['cached_keys'] == 1

    def test_cache_stats_after_hit_and_miss(self):
        """캐시 히트/미스 혼합 시 통계."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 fetch: miss
        feed.fetch("BTC/USDT", "1h", limit=500)
        # 두 번째 fetch (같은 심볼/타임프레임): hit
        feed.fetch("BTC/USDT", "1h", limit=500)
        # 새로운 심볼: miss
        feed.fetch("ETH/USDT", "1h", limit=500)
        
        stats = feed.cache_stats()
        
        assert stats['hit_count'] == 1
        assert stats['miss_count'] == 2
        assert stats['total'] == 3
        assert stats['hit_rate'] == 1/3
        assert stats['cached_keys'] == 2

    def test_cache_stats_hit_rate_100_percent(self):
        """캐시 히트율 100% 케이스."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 fetch: miss
        feed.fetch("BTC/USDT", "1h", limit=500)
        # 3번 반복 hit
        for _ in range(3):
            feed.fetch("BTC/USDT", "1h", limit=500)
        
        stats = feed.cache_stats()
        
        assert stats['hit_count'] == 3
        assert stats['miss_count'] == 1
        assert stats['total'] == 4
        assert stats['hit_rate'] == 0.75
        assert stats['cached_keys'] == 1



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
