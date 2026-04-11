# Cycle 26 - liquidation_feed.py 견고성 개선 완료

## 이번 작업 내용
Cycle 6 패턴 (exponential backoff + fallback) 적용으로 `liquidation_feed.py` 견고성 향상.

**수정:**
1. `src/data/liquidation_feed.py`
   - L29-36: `_MAX_RETRIES`, `_RETRY_BACKOFF_SECONDS` 상수 추가
   - L43-46: `LiquidationFetcher.__init__()` 에 `max_retries`, `_last_successful` 필드 추가
   - L55-102: `get_recent()` 재시도 + fallback 로직 구현
     - 재시도: exponential backoff (1s, 2s)
     - 실패 시: 마지막 성공값 fallback → 빈 리스트

**테스트:**
1. 기존 14개 테스트 모두 통과 (backward compatible)
2. 신규 2개 테스트 추가:
   - `test_get_recent_retry_fallback`: API 재시도 실패 → fallback 동작
   - `test_get_recent_retry_success_on_second_attempt`: 첫 실패 → 두 번째 성공

## 테스트 결과
```
tests/test_liquidation_cascade.py: 16 passed in 7.76s
```

## 다음 단계
- 캐시 key 충돌 방지: 여러 심볼 동시 캐시 시 key 정확성 검증
- 데이터 피드 통합: health_check와 retry 상태 연동
