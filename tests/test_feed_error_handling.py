"""
Comprehensive error handling and circuit breaker tests for DataFeed.
Tests: retry logic, circuit breaker, rate limiting, connection failures.
"""

import pytest
from unittest.mock import MagicMock, patch
import time

from src.data.feed import (
    DataFeed,
    CircuitBreaker,
    CircuitState,
    _is_transient_error,
    _is_fatal_error,
    _is_rate_limit_error,
    _backoff_with_rate_limit,
)

try:
    import ccxt
except ImportError:
    ccxt = None


class TestErrorClassification:
    """Error classification functions."""
    
    def test_is_transient_network_error(self):
        """Network errors should be transient."""
        assert _is_transient_error(TimeoutError("timeout")) is True
        assert _is_transient_error(ConnectionError("no connection")) is True
    
    def test_is_fatal_value_error(self):
        """ValueError should be fatal."""
        assert _is_fatal_error(ValueError("bad symbol")) is True
        assert _is_fatal_error(KeyError("missing key")) is True
    
    def test_is_rate_limit_error(self):
        """Rate limit error detection."""
        if ccxt is None:
            assert _is_rate_limit_error(RuntimeError("something")) is False
            return
        
        assert _is_rate_limit_error(ccxt.RateLimitExceeded("rate limit")) is True
        assert _is_rate_limit_error(ccxt.NetworkError("network")) is False


class TestCircuitBreaker:
    """Circuit breaker state machine tests."""
    
    def test_initial_state_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0
        assert cb._success_count == 0
    
    def test_can_attempt_when_closed(self):
        """Can attempt when CLOSED."""
        cb = CircuitBreaker()
        assert cb.can_attempt() is True
    
    def test_record_success_closed_state(self):
        """Record success in CLOSED state resets failures."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb._failure_count == 2
        
        cb.record_success()
        assert cb._failure_count == 0
        assert cb._success_count == 1
    
    def test_transition_closed_to_open(self):
        """Transition: CLOSED -> OPEN after N failures."""
        cb = CircuitBreaker(failure_threshold=3)
        
        # Record failures
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_attempt() is False
    
    def test_transition_open_to_half_open(self):
        """Transition: OPEN -> HALF_OPEN after recovery timeout."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.5,
            success_threshold=2
        )
        
        # Move to OPEN
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.6)
        
        # Should auto-transition to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.can_attempt() is True
    
    def test_transition_half_open_to_closed(self):
        """Transition: HALF_OPEN -> CLOSED after N successes."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.5,
            success_threshold=2
        )
        
        # Move to OPEN
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        
        # Wait and move to HALF_OPEN
        time.sleep(0.6)
        assert cb.state == CircuitState.HALF_OPEN
        
        # Record successes
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED


class TestDataFeedCircuitBreaker:
    """DataFeed integration with circuit breaker."""
    
    def test_fetch_with_circuit_breaker_closed(self):
        """Fetch works normally when circuit breaker is CLOSED."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 42300, 100]
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        assert result.symbol == "BTC/USDT"
        assert result.candles == 1
        assert feed.circuit_breaker_status()['state'] == 'closed'
    
    def test_fetch_rejected_when_circuit_open(self):
        """Fetch raises error when circuit breaker is OPEN."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = Exception("API error")
        
        feed = DataFeed(connector)
        feed._circuit_breaker = CircuitBreaker(failure_threshold=1)
        
        # First failure: opens circuit
        with pytest.raises(Exception, match="API error"):
            feed.fetch("BTC/USDT", "1h")
        
        # Circuit is now OPEN
        assert feed.circuit_breaker_status()['state'] == 'open'
        
        # Next fetch should be rejected immediately
        with pytest.raises(RuntimeError, match="circuit breaker OPEN"):
            feed.fetch("BTC/USDT", "1h")


class TestRetryLogic:
    """Retry mechanism with exponential backoff."""
    
    def test_retry_on_transient_error(self):
        """Transient errors trigger retry."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            TimeoutError("timeout"),
            [[1704067200000, 42000, 42500, 41800, 42300, 100]]
        ]
        
        feed = DataFeed(connector, max_retries=3)
        result = feed.fetch("BTC/USDT", "1h")
        
        assert result.symbol == "BTC/USDT"
        assert connector.fetch_ohlcv.call_count == 2
    
    def test_no_retry_on_fatal_error(self):
        """Fatal errors are not retried."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = ValueError("bad symbol")

        feed = DataFeed(connector, max_retries=3)

        with pytest.raises(ValueError):
            feed.fetch("BXX/USDT", "1h")

        assert connector.fetch_ohlcv.call_count == 1


class TestExchangeFallback:
    """DataFeed public exchange fallback tests."""

    _CANDLE = [[1704067200000, 42000, 42500, 41800, 42300, 100]]

    def _make_feed(self, fallback_ids=None):
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        return DataFeed(connector, max_retries=1, fallback_exchange_ids=fallback_ids or [])

    def test_fallback_succeeds_when_primary_fails(self):
        """Primary connector timeout → fallback exchange fetch succeeds."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=["binance"])

        with patch.object(feed, "_fetch_public_ohlcv", return_value=self._CANDLE) as mock_pub:
            result = feed.fetch("BTC/USDT", "1h")

        assert result.symbol == "BTC/USDT"
        mock_pub.assert_called_once_with("binance", "BTC/USDT", "1h", 500)
        assert feed._exchange_fallback_count == 1

    def test_fallback_tries_multiple_exchanges(self):
        """First fallback exchange fails → second succeeds."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=["binance", "okx"])

        call_results = [ValueError("binance error"), self._CANDLE]

        def side_effect(exchange_id, *args, **kwargs):
            res = call_results.pop(0)
            if isinstance(res, Exception):
                raise res
            return res

        with patch.object(feed, "_fetch_public_ohlcv", side_effect=side_effect):
            result = feed.fetch("BTC/USDT", "1h")

        assert result.symbol == "BTC/USDT"
        assert feed._exchange_fallback_count == 1

    def test_fallback_raises_when_all_exchanges_fail(self):
        """All fallback exchanges fail → last exception raised."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=["binance", "okx"])

        with patch.object(feed, "_fetch_public_ohlcv", side_effect=ValueError("all failed")):
            with pytest.raises(Exception):
                feed.fetch("BTC/USDT", "1h")

    def test_no_fallback_when_list_empty(self):
        """Empty fallback list → original error propagates."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=[])

        with pytest.raises(TimeoutError):
            feed.fetch("BTC/USDT", "1h")

    def test_fatal_error_does_not_trigger_fallback(self):
        """Fatal errors (ValueError) skip fallback even if configured."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = ValueError("bad symbol")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=["binance"])

        with patch.object(feed, "_fetch_public_ohlcv") as mock_pub:
            with pytest.raises(ValueError):
                feed.fetch("BAD/SYM", "1h")

        mock_pub.assert_not_called()

    def test_exchange_fallback_count_in_cache_stats(self):
        """exchange_fallback_count는 cache_stats()에 포함된다."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL timeout")
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=["binance"])

        with patch.object(feed, "_fetch_public_ohlcv", return_value=self._CANDLE):
            feed.fetch("BTC/USDT", "1h")

        stats = feed.cache_stats()
        assert "exchange_fallback_count" in stats
        assert stats["exchange_fallback_count"] == 1

    def test_default_fallback_exchanges_list(self):
        """기본값(fallback_exchange_ids 미지정)은 빈 목록."""
        connector = MagicMock()
        feed = DataFeed(connector)
        assert feed._fallback_exchange_ids == []

    def test_explicit_fallback_exchanges_list(self):
        """명시적으로 전달한 fallback 목록이 사용된다."""
        connector = MagicMock()
        feed = DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)
        assert "binance" in feed._fallback_exchange_ids
        assert "okx" in feed._fallback_exchange_ids


class TestFallbackExhaustedStaleCacheFallback:
    """exchange fallback 전부 실패 시 stale cache로 복구하는 시나리오."""

    _CANDLE = [[1704067200000, 42000, 42500, 41800, 42300, 100]]

    def _make_feed_with_stale(self, fallback_ids=None):
        """초기 성공 fetch로 stale cache를 채운 뒤, 이후 항상 실패하는 feed 반환."""
        connector = MagicMock()
        # 첫 호출: 성공 (stale cache 채움)
        connector.fetch_ohlcv.return_value = self._CANDLE
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=fallback_ids or [])
        feed.fetch("BTC/USDT", "1h", limit=1)
        # 이후: connector 실패
        connector.fetch_ohlcv.side_effect = TimeoutError("SSL blocked")
        return feed

    def test_all_fallbacks_fail_uses_stale_cache(self):
        """primary + 모든 fallback 실패 → stale cache 반환."""
        feed = self._make_feed_with_stale(fallback_ids=["binance", "okx"])
        # force cache expiry
        feed._cache.clear()

        with patch.object(feed, "_fetch_public_ohlcv", side_effect=ValueError("no data")):
            result = feed.fetch("BTC/USDT", "1h", limit=1)

        assert result is not None
        assert result.symbol == "BTC/USDT"
        assert feed._fallback_count >= 1

    def test_stale_cache_not_used_when_no_fallbacks_configured(self):
        """fallback 목록이 비어있으면 non-transient error 시 stale cache 미사용."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._CANDLE
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=[])
        feed.fetch("BTC/USDT", "1h", limit=1)
        feed._cache.clear()
        connector.fetch_ohlcv.side_effect = ValueError("fatal error")

        with pytest.raises(ValueError):
            feed.fetch("BTC/USDT", "1h", limit=1)

    def test_transient_error_still_uses_stale_cache_without_fallbacks(self):
        """fallback 없어도 transient error이면 stale cache 시도 (기존 동작 유지)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = self._CANDLE
        feed = DataFeed(connector, max_retries=1, fallback_exchange_ids=[])
        feed.fetch("BTC/USDT", "1h", limit=1)
        feed._cache.clear()
        connector.fetch_ohlcv.side_effect = TimeoutError("timeout")

        result = feed.fetch("BTC/USDT", "1h", limit=1)
        assert result is not None
        assert feed._fallback_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
