"""
News duplicate detection tests.
"""

import pytest
import time
from src.data.news import NewsMonitor, NewsEvent, _get_title_hash


class TestNewsDuplicate:
    """NewsMonitor 중복 감지 테스트."""

    def test_title_hash_consistency(self):
        """동일 제목 → 동일 hash."""
        title1 = "Bitcoin crashes hard"
        title2 = "BITCOIN CRASHES HARD"  # 대소문자 다름
        
        hash1 = _get_title_hash(title1)
        hash2 = _get_title_hash(title2)
        assert hash1 == hash2, "Title hash should be case-insensitive"
        
    def test_title_hash_whitespace_trim(self):
        """공백 제거 후 hash."""
        title1 = "Bitcoin crashes"
        title2 = "  Bitcoin crashes  "  # 앞뒤 공백
        
        hash1 = _get_title_hash(title1)
        hash2 = _get_title_hash(title2)
        assert hash1 == hash2, "Title hash should trim whitespace"

    def test_duplicate_detection_same_headline(self):
        """동일 헤드라인 → 중복 감지."""
        monitor = NewsMonitor(duplicate_window_hours=24)
        
        # 첫 번째 이벤트
        event1 = monitor.mock(level="HIGH", event_text="Bitcoin exchange hack")
        assert not monitor._is_duplicate(event1.title_hash)
        
        # 해시 등록
        monitor._seen_hashes[event1.title_hash] = time.time()
        
        # 두 번째 동일 헤드라인
        event2 = monitor.mock(level="HIGH", event_text="Bitcoin exchange hack")
        assert monitor._is_duplicate(event2.title_hash), "Should detect duplicate"

    def test_duplicate_detection_case_insensitive(self):
        """대소문자 무관하게 중복 감지."""
        monitor = NewsMonitor(duplicate_window_hours=24)
        
        event1 = monitor.mock(level="HIGH", event_text="BTC HACK")
        monitor._seen_hashes[event1.title_hash] = time.time()
        
        event2 = monitor.mock(level="HIGH", event_text="btc hack")
        assert monitor._is_duplicate(event2.title_hash)

    def test_duplicate_detection_mixed_case_and_whitespace(self):
        """대소문자 + 공백 차이 무관하게 중복 감지."""
        monitor = NewsMonitor(duplicate_window_hours=24)
        
        event1 = monitor.mock(level="HIGH", event_text="  BTC  HACK  ")
        monitor._seen_hashes[event1.title_hash] = time.time()
        
        event2 = monitor.mock(level="HIGH", event_text="btc hack")
        assert monitor._is_duplicate(event2.title_hash), "Should detect duplicate with case and whitespace differences"

    def test_no_duplicate_different_headlines(self):
        """다른 헤드라인 → 중복 없음."""
        monitor = NewsMonitor(duplicate_window_hours=24)
        
        event1 = monitor.mock(level="HIGH", event_text="Bitcoin hack")
        monitor._seen_hashes[event1.title_hash] = time.time()
        
        event2 = monitor.mock(level="HIGH", event_text="Ethereum hack")
        assert not monitor._is_duplicate(event2.title_hash)

    def test_duplicate_window_expiration(self):
        """중복 윈도우 외 → 중복 아님."""
        monitor = NewsMonitor(duplicate_window_hours=1)  # 1시간
        
        event1 = monitor.mock(level="HIGH", event_text="Bitcoin hack")
        past_time = time.time() - 3600 - 60  # 1시간 1분 전
        monitor._seen_hashes[event1.title_hash] = past_time
        
        # cleanup 실행
        monitor._cleanup_old_hashes(time.time())
        
        # 윈도우 외이므로 중복 아님
        assert not monitor._is_duplicate(event1.title_hash)

    def test_hash_empty_title(self):
        """빈 제목 hash."""
        hash_val = _get_title_hash("")
        assert isinstance(hash_val, str)
        assert len(hash_val) == 32  # MD5 hex length

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
