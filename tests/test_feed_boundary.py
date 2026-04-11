"""
_fetch_fresh 경계 테스트: NaN/공 DataFrame 처리
"""

from unittest.mock import MagicMock
import pandas as pd
import pytest

from src.data.feed import DataFeed


class TestFetchFreshBoundaries:
    """_fetch_fresh 경계 조건 테스트."""

    def test_fetch_fresh_empty_dataframe(self):
        """빈 raw 데이터 → ValueError 발생."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = []  # 빈 리스트
        
        feed = DataFeed(connector)
        
        # 수정된 동작: ValueError 발생 (명확한 에러)
        with pytest.raises(ValueError, match="Empty OHLCV data"):
            feed.fetch("BTC/USDT", "1h", limit=500)

    def test_fetch_fresh_single_candle_with_nan(self):
        """단일 캔들 NaN 데이터 → 지표 계산 및 summary 반환."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, float('nan'), 100],  # NaN close
        ]
        
        feed = DataFeed(connector)
        result = feed.fetch("BTC/USDT", "1h", limit=500)
        
        # DataSummary 정상 생성 (NaN값이 있어도 반환)
        assert result.symbol == "BTC/USDT"
        assert result.candles == 1
        assert pd.isna(result.df['close'].iloc[0])
        # 지표는 모두 계산됨
        assert 'ema20' in result.df.columns
        assert 'rsi14' in result.df.columns
        assert 'atr14' in result.df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestCacheTTLBoundaries:
    """캐시 TTL 경계 조건 테스트."""

    def test_cache_ttl_zero_disables_cache(self):
        """ttl=0 → 캐시 비활성화 (모든 요청이 미스)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        
        feed = DataFeed(connector, cache_ttl=0)
        
        # 첫 fetch
        result1 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert result1.symbol == "BTC/USDT"
        assert feed.cache_stats()['hit_count'] == 0
        assert feed.cache_stats()['miss_count'] == 1
        
        # 동일 key로 두 번째 fetch → ttl=0이므로 캐시 무효
        result2 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['hit_count'] == 0
        assert feed.cache_stats()['miss_count'] == 2
        
        # fetch_ohlcv 호출이 2번
        assert connector.fetch_ohlcv.call_count == 2

    def test_cache_ttl_very_large_value(self):
        """ttl=999999999 → 캐시 거의 항상 유효 (테스트 범위 내)."""
        connector = MagicMock()
        connector.fetch_ohlcv.return_value = [
            [1704067200000, 42000, 42500, 41800, 41900, 100],
        ]
        
        feed = DataFeed(connector, cache_ttl=999999999)
        
        # 첫 fetch
        result1 = feed.fetch("BTC/USDT", "1h", limit=500)
        assert feed.cache_stats()['miss_count'] == 1
        
        # 동일 key로 10번 fetch → 모두 캐시 히트
        for _ in range(10):
            result = feed.fetch("BTC/USDT", "1h", limit=500)
            assert result.symbol == "BTC/USDT"
        
        assert feed.cache_stats()['hit_count'] == 10
        assert feed.cache_stats()['miss_count'] == 1
        
        # fetch_ohlcv 호출은 1번만
        assert connector.fetch_ohlcv.call_count == 1
