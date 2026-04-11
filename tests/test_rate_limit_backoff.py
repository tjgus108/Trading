"""
Rate limit backoff 테스트.
RateLimitExceeded 감지 시 긴 backoff 사용 검증.
"""

from unittest.mock import MagicMock, patch
import ccxt
import pytest

from src.data.feed import DataFeed, _is_rate_limit_error, _backoff_with_rate_limit


class TestRateLimitBackoff:
    """Rate limit 에러 처리 테스트."""

    def test_is_rate_limit_error(self):
        """RateLimitExceeded 감지."""
        error = ccxt.RateLimitExceeded("Rate limit exceeded")
        assert _is_rate_limit_error(error) is True
        
        # 다른 에러는 False
        assert _is_rate_limit_error(ccxt.NetworkError("Network error")) is False
        assert _is_rate_limit_error(Exception("Generic error")) is False

    def test_backoff_with_rate_limit_long_wait(self):
        """RateLimitExceeded는 긴 backoff 사용."""
        error = ccxt.RateLimitExceeded("Rate limit")
        
        with patch("src.data.feed.time.sleep") as mock_sleep:
            with patch("src.data.feed.logger") as mock_logger:
                _backoff_with_rate_limit(error, attempt=1)
        
        # 첫 시도: 2 + 1*2 = 4초
        mock_sleep.assert_called_once_with(4)
        # 로그 기록
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0]
        assert "RateLimitExceeded detected" in call_args[0]
        assert call_args[1] == 4  # wait_time
        assert call_args[2] == 1  # attempt

    def test_backoff_with_rate_limit_increasing(self):
        """RateLimitExceeded backoff는 증가 (2s, 4s, 6s)."""
        error = ccxt.RateLimitExceeded("Rate limit")
        
        wait_times = []
        with patch("src.data.feed.time.sleep") as mock_sleep:
            with patch("src.data.feed.logger"):
                for attempt in range(1, 4):
                    _backoff_with_rate_limit(error, attempt)
                    wait_times.append(mock_sleep.call_args[0][0])
        
        assert wait_times == [4, 6, 8]  # 2+1*2, 2+2*2, 2+3*2

    def test_backoff_with_other_transient_error(self):
        """다른 transient 에러는 짧은 backoff (0.5s * attempt)."""
        error = ccxt.NetworkError("Network error")
        
        with patch("src.data.feed.time.sleep") as mock_sleep:
            with patch("src.data.feed.logger"):
                _backoff_with_rate_limit(error, attempt=2)
        
        # 두 번째 시도: 0.5 * 2 = 1초
        mock_sleep.assert_called_once_with(1.0)

    def test_fetch_with_rate_limit_retry(self):
        """RateLimitExceeded 시 긴 backoff와 함께 재시도."""
        connector = MagicMock()
        connector.fetch_ohlcv.side_effect = [
            ccxt.RateLimitExceeded("Rate limit exceeded"),
            [[1704067200000, 42000, 42500, 41800, 42300, 100]],
        ]
        
        feed = DataFeed(connector, max_retries=2)
        
        with patch("src.data.feed._backoff_with_rate_limit") as mock_backoff:
            result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # backoff 호출 확인 (attempt=1)
        mock_backoff.assert_called_once()
        call_args = mock_backoff.call_args[0]
        assert isinstance(call_args[0], ccxt.RateLimitExceeded)
        assert call_args[1] == 1  # attempt
        
        # 성공 결과
        assert result.symbol == "BTC/USDT"
        assert result.candles == 1

    def test_fetch_with_rate_limit_exhausted(self):
        """RateLimitExceeded 재시도 모두 실패."""
        connector = MagicMock()
        error = ccxt.RateLimitExceeded("Rate limit exceeded")
        connector.fetch_ohlcv.side_effect = error
        
        feed = DataFeed(connector, max_retries=2)
        
        with patch("src.data.feed._backoff_with_rate_limit") as mock_backoff:
            with patch("src.data.feed.logger") as mock_logger:
                with pytest.raises(ccxt.RateLimitExceeded):
                    feed.fetch("BTC/USDT", "1h", limit=500)
        
        # 2회 backoff 호출 (attempt 1, 2)
        assert mock_backoff.call_count == 1
        
        # exhausted 로그 확인
        error_logs = mock_logger.error.call_args_list
        assert len(error_logs) >= 1
        call_args = error_logs[0][0]
        assert "Fetch exhausted" in call_args[0]
        assert "RateLimitExceeded" in call_args[5]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
