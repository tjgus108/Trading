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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
