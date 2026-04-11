# Cycle 31 - DataFeed 에러 로그 개선

## 이번 작업 내용
DataFeed fetch 실패 시 에러 로그에 더 많은 컨텍스트 추가.

### 변경 사항

**src/data/feed.py (L70-77)**
- Error 로그 포맷 개선
- 기존: `"Fetch failed for %s %s after %d attempts: %s"` (symbol, timeframe, max_retries, error)
- 신규: `"Fetch exhausted: symbol=%s, timeframe=%s, limit=%d, max_retries=%d, error_type=%s, message=%s"`
- 추가 정보:
  - `limit`: 요청한 캔들 개수
  - `error_type`: 예외 타입 (ValueError, TimeoutError 등)
  - 구조화된 포맷으로 로그 파싱 용이

**tests/test_feed_parallel.py**
- `test_fetch_max_retries_exceeded` 업데이트 (새 포맷에 맞춤)
- `test_fetch_error_log_includes_context` 신규 추가
  - 에러 로그 포맷 검증
  - 모든 컨텍스트 필드 확인

### 테스트 결과
- test_feed_parallel.py: 10/10 passed
- 관련 데이터 fetch 테스트: 모두 통과

## 다음 단계
- Cycle 32: Notifier에 cycle context 추가, 또는 캐시 통계 기능 추가
