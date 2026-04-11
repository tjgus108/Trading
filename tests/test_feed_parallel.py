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

    def test_cache_key_no_collision_multi_symbol(self):
        """서로 다른 심볼/타임프레임 동시 페치 시 캐시 키 (symbol, timeframe, limit) 튜플 충돌 없음."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            # BTC/USDT 1h
            [[1704067200000, 42000, 42500, 41800, 42300, 100]],
            # ETH/USDT 1h
            [[1704067200000, 2500, 2600, 2450, 2550, 500]],
            # BTC/USDT 4h
            [[1704067200000, 41000, 43000, 40800, 42100, 150]],
            # ETH/USDT 4h
            [[1704067200000, 2400, 2700, 2350, 2480, 600]],
        ]

        feed = DataFeed(connector, cache_ttl=60)
        
        # 다양한 심볼과 타임프레임 조합 페치
        btc_1h = feed.fetch("BTC/USDT", "1h", limit=500)
        eth_1h = feed.fetch("ETH/USDT", "1h", limit=500)
        btc_4h = feed.fetch("BTC/USDT", "4h", limit=500)
        eth_4h = feed.fetch("ETH/USDT", "4h", limit=500)

        # 각 캐시 키가 서로 다른지 검증
        assert btc_1h.symbol == "BTC/USDT" and btc_1h.timeframe == "1h"
        assert eth_1h.symbol == "ETH/USDT" and eth_1h.timeframe == "1h"
        assert btc_4h.symbol == "BTC/USDT" and btc_4h.timeframe == "4h"
        assert eth_4h.symbol == "ETH/USDT" and eth_4h.timeframe == "4h"

        # 캐시 통계: 4개 심볼/타임프레임 조합 → 4개 미스
        stats = feed.cache_stats()
        assert stats['miss_count'] == 4, "4개 모두 캐시 미스 (서로 다른 키)"
        assert stats['cached_keys'] == 4, "4개의 서로 다른 캐시 키 생성"
        assert connector.fetch_ohlcv.call_count == 4, "API 호출 4회"

        # 같은 조합 다시 페치 → 캐시 히트 확인
        btc_1h_again = feed.fetch("BTC/USDT", "1h", limit=500)
        
        stats_after_hit = feed.cache_stats()
        assert stats_after_hit['hit_count'] == 1, "캐시 히트 1회"
        assert stats_after_hit['cached_keys'] == 4, "캐시 키 개수 변화 없음"
        assert connector.fetch_ohlcv.call_count == 4, "API 호출 증가 없음"
        
        # 히트된 데이터가 원래 데이터와 동일한지 검증
        assert btc_1h_again.symbol == btc_1h.symbol
        assert btc_1h_again.timeframe == btc_1h.timeframe
        assert btc_1h_again.candles == btc_1h.candles



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
        """Transient 에러 모두 실패 시 exhausted 로그에 context 포함."""
        import ccxt
        connector = MagicMock()
        error = ccxt.NetworkError("Connection failed")
        connector.fetch_ohlcv.side_effect = error

        feed = DataFeed(connector, max_retries=3)
        
        with patch("src.data.feed.logger") as mock_logger:
            with pytest.raises(ccxt.NetworkError):
                feed.fetch("BTC/USDT", "1h", limit=500)
            
            # Error 로그 확인 (exhausted)
            error_calls = mock_logger.error.call_args_list
            assert len(error_calls) >= 1
            
            error_call = error_calls[0]
            call_args = error_call[0]  # (format_string, arg1, arg2, ...)
            
            # Exhausted 포맷 확인
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
            assert call_args[5] == "NetworkError"  # error_type
            assert "Connection failed" in call_args[6]  # message
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



    def test_fetch_multiple_cache_stats_integration(self):
        """fetch_multiple 사용 시 cache_stats가 정확히 기록되는지 검증."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 번째 fetch_multiple: 2개 심볼 → miss 2
        symbols = ["BTC/USDT", "ETH/USDT"]
        results1 = feed.fetch_multiple(symbols, "1h", limit=500)
        
        stats_after_first = feed.cache_stats()
        assert stats_after_first['miss_count'] == 2, "첫 번째 호출: miss 2"
        assert stats_after_first['hit_count'] == 0, "첫 번째 호출: hit 0"
        assert stats_after_first['total'] == 2
        assert stats_after_first['cached_keys'] == 2
        
        # 두 번째 fetch_multiple (같은 심볼): → hit 2
        results2 = feed.fetch_multiple(symbols, "1h", limit=500)
        
        stats_after_second = feed.cache_stats()
        assert stats_after_second['miss_count'] == 2, "두 번째 호출: miss는 여전히 2"
        assert stats_after_second['hit_count'] == 2, "두 번째 호출: hit 2"
        assert stats_after_second['total'] == 4
        assert stats_after_second['cached_keys'] == 2
        assert stats_after_second['hit_rate'] == 0.5

    def test_fetch_multiple_partial_cache_hit(self):
        """fetch_multiple에서 일부만 캐시 히트되는 경우."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 호출: BTC/USDT만 캐시
        feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 1
        
        # fetch_multiple: BTC(hit) + ETH(miss)
        results = feed.fetch_multiple(["BTC/USDT", "ETH/USDT"], "1h", limit=500)
        
        stats = feed.cache_stats()
        assert stats['hit_count'] == 1, "BTC는 캐시 히트"
        assert stats['miss_count'] == 2, "ETH는 새로운 미스"
        assert stats['total'] == 3
        assert stats['hit_rate'] == 1/3
        assert len(results) == 2

    def test_cache_ttl_boundary_before_expiry(self):
        """TTL 만료 직전: 캐시 히트 (now - ts < ttl)."""
        from unittest.mock import MagicMock, patch
        
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # Mock time을 사용해 정확한 경계 조건 제어
        with patch("src.data.feed.time.time") as mock_time:
            # 첫 fetch: miss (t=0)
            mock_time.return_value = 1000.0
            feed.fetch("BTC/USDT", "1h", limit=500)
            assert feed.cache_stats()['miss_count'] == 1
            
            # TTL 만료 직전 (t=59, 1000 + 59 = 1059, 조건 59 < 60은 참)
            mock_time.return_value = 1059.0
            result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        stats = feed.cache_stats()
        assert stats['hit_count'] == 1, "59초 경과 시 캐시 히트"
        assert stats['miss_count'] == 1, "미스 수 변화 없음"
        assert connector.fetch_ohlcv.call_count == 1, "API 호출 없음"

    def test_cache_ttl_boundary_exactly_expired(self):
        """TTL 정확히 만료: 캐시 미스 (now - ts >= ttl)."""
        import time
        from unittest.mock import MagicMock, patch
        
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # Mock time을 사용해 정확한 경계 조건 제어
        with patch("src.data.feed.time.time") as mock_time:
            # 첫 fetch: miss (t=0)
            mock_time.return_value = 1000.0
            feed.fetch("BTC/USDT", "1h", limit=500)
            assert feed.cache_stats()['miss_count'] == 1
            
            # TTL 정확히 만료 (t=60, 0 + 60 = 60, 조건 60 < 60은 거짓)
            mock_time.return_value = 1060.0
            result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        stats = feed.cache_stats()
        assert stats['hit_count'] == 0, "정확히 만료 시 캐시 미스"
        assert stats['miss_count'] == 2, "새로운 미스 기록"
        assert connector.fetch_ohlcv.call_count == 2, "API 재호출"



if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestErrorClassification:
    """에러 분류 (Transient vs Fatal) 테스트."""

    def test_transient_network_error_retry(self):
        """NetworkError는 transient → 재시도."""
    def test_transient_network_error_retry(self):
        """NetworkError는 transient → 재시도."""
        import ccxt
        from unittest.mock import MagicMock, patch

        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            ccxt.NetworkError("Connection failed"),
            [[1704067200000, 42000, 42500, 41800, 42300, 100]],
        ]

        feed = DataFeed(connector, max_retries=2)
        
        with patch("src.data.feed.logger"):
            result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # 첫 시도 실패 후 두 번째 시도에서 성공
        assert result.symbol == "BTC/USDT"
        assert result.candles == 1
        assert connector.fetch_ohlcv.call_count == 2

    def test_fatal_bad_symbol_no_retry(self):
        """BadSymbol은 fatal → 즉시 중단."""
        import ccxt
        from unittest.mock import MagicMock, patch

        connector = MagicMock()
        error = ccxt.BadSymbol("Invalid symbol: FAKE/USDT")
        connector.fetch_ohlcv.side_effect = error

        feed = DataFeed(connector, max_retries=3)
        
        with patch("src.data.feed.logger"):
            with pytest.raises(ccxt.BadSymbol):
                feed.fetch("FAKE/USDT", "1h", limit=500)
        
        # 재시도하지 않음 (call_count = 1)
        assert connector.fetch_ohlcv.call_count == 1

    def test_fetch_multiple_cache_stats_integration(self):
        """fetch_multiple 사용 시 cache_stats가 정확히 기록되는지 검증."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 번째 fetch_multiple: 2개 심볼 → miss 2
        symbols = ["BTC/USDT", "ETH/USDT"]
        results1 = feed.fetch_multiple(symbols, "1h", limit=500)
        
        stats_after_first = feed.cache_stats()
        assert stats_after_first['miss_count'] == 2, "첫 번째 호출: miss 2"
        assert stats_after_first['hit_count'] == 0, "첫 번째 호출: hit 0"
        assert stats_after_first['total'] == 2
        assert stats_after_first['cached_keys'] == 2
        
        # 두 번째 fetch_multiple (같은 심볼): → hit 2
        results2 = feed.fetch_multiple(symbols, "1h", limit=500)
        
        stats_after_second = feed.cache_stats()
        assert stats_after_second['miss_count'] == 2, "두 번째 호출: miss는 여전히 2"
        assert stats_after_second['hit_count'] == 2, "두 번째 호출: hit 2"
        assert stats_after_second['total'] == 4
        assert stats_after_second['cached_keys'] == 2
        assert stats_after_second['hit_rate'] == 0.5

    def test_fetch_multiple_partial_cache_hit(self):
        """fetch_multiple에서 일부만 캐시 히트되는 경우."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector, cache_ttl=60)
        
        # 첫 호출: BTC/USDT만 캐시
        feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 1
        
        # fetch_multiple: BTC(hit) + ETH(miss)
        results = feed.fetch_multiple(["BTC/USDT", "ETH/USDT"], "1h", limit=500)
        
        stats = feed.cache_stats()
        assert stats['hit_count'] == 1, "BTC는 캐시 히트"
        assert stats['miss_count'] == 2, "ETH는 새로운 미스"
        assert stats['total'] == 3
        assert stats['hit_rate'] == 1/3
        assert len(results) == 2
