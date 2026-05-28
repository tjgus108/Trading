"""DataFeed 캐시 hit/miss 카운터 테스트 (Cycle 239)."""

import pytest
from unittest.mock import MagicMock

from src.data.feed import DataFeed


def _make_feed(cache_ttl: int = 60) -> DataFeed:
    """테스트용 DataFeed 생성 (mock connector)."""
    connector = MagicMock()
    connector.fetch_ohlcv.return_value = [
        [1704067200000, 42000, 42500, 41800, 42100, 100],
        [1704070800000, 42100, 42600, 41900, 42300, 120],
    ]
    return DataFeed(connector, cache_ttl=cache_ttl)


class TestDataFeedCacheStats:
    """get_cache_stats() 메서드 검증."""

    def test_initial_cache_stats_zero(self):
        """초기 상태: hits=0, misses=0, hit_rate=0.0."""
        feed = _make_feed()
        stats = feed.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0.0

    def test_cache_miss_increments(self):
        """첫 fetch → cache miss 1회."""
        feed = _make_feed()
        feed.fetch("BTC/USDT", "1h", limit=500)
        stats = feed.get_cache_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
        assert stats["hit_rate"] == 0.0

    def test_cache_hit_increments(self):
        """동일 키 두 번 fetch → 1 miss + 1 hit."""
        feed = _make_feed(cache_ttl=3600)
        feed.fetch("BTC/USDT", "1h", limit=500)
        feed.fetch("BTC/USDT", "1h", limit=500)
        stats = feed.get_cache_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 1
        assert abs(stats["hit_rate"] - 0.5) < 0.01

    def test_hit_rate_calculation(self):
        """hit_rate = hits / (hits + misses)."""
        feed = _make_feed(cache_ttl=3600)
        # 3개 서로 다른 키 → 3 misses
        feed.fetch("BTC/USDT", "1h", limit=500)
        feed.fetch("ETH/USDT", "1h", limit=500)
        feed.fetch("SOL/USDT", "1h", limit=500)
        # 기존 키 반복 → 3 hits
        feed.fetch("BTC/USDT", "1h", limit=500)
        feed.fetch("ETH/USDT", "1h", limit=500)
        feed.fetch("SOL/USDT", "1h", limit=500)
        stats = feed.get_cache_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 3
        assert abs(stats["hit_rate"] - 0.5) < 0.01

    def test_cache_stats_dict_keys(self):
        """get_cache_stats() 반환 dict에 필수 키 존재."""
        feed = _make_feed()
        stats = feed.get_cache_stats()
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats

    def test_cache_stats_consistent_with_cache_stats_method(self):
        """get_cache_stats()가 기존 cache_stats()와 일관성 유지."""
        feed = _make_feed(cache_ttl=3600)
        feed.fetch("BTC/USDT", "1h", limit=500)
        feed.fetch("BTC/USDT", "1h", limit=500)

        new_stats = feed.get_cache_stats()
        old_stats = feed.cache_stats()

        # _cache_hits == _hit_count, _cache_misses == _miss_count
        assert new_stats["hits"] == old_stats["hit_count"]
        assert new_stats["misses"] == old_stats["miss_count"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
