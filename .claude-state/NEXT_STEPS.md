# Cycle 24 - Category C: Data & Infrastructure

## 완료: Data feeds health_check 통합 강화

### 이번 작업 내용
Data feeds 상태를 종합하는 health_check 시스템 검증 및 개선.

**변경 사항:**
1. `src/data/health_check.py` (L146-166)
   - _check_single() 메서드 리팩토링
   - feed_type이 명시적으로 지정되면 우선 사용 (테스트 안정성)
   - feed_type="unknown"일 때만 hasattr 기반 자동 감지
   - 순환 호출 및 MagicMock 간섭 제거

2. `src/data/health_check.py` (L139-140)
   - anomaly 감지 로직 수정
   - fallback_count > 0 → "operating_in_degraded_mode" 추가 (조건 완화)

3. `src/data/health_check.py` (L225-228)
   - WebSocket feed 상태 판단 순서 변경
   - retry_count >= max_retry 확인을 candle_count 체크 전에 배치
   - 최대 재시도 초과 시 정확히 DISCONNECTED 반환

4. `src/data/__init__.py`
   - health_check 관련 클래스 export (DataFeedsHealthCheck 등)

### 테스트 결과
```
tests/test_data_health_check.py: 17 passed in 0.98s
- FeedHealthReport: 3 passed
- DataHealthCheck: 3 passed
- DataFeedsHealthCheck: 11 passed
  ├ register/basic checks: 1 passed
  ├ REST feed: 1 passed
  ├ WebSocket feed (connected/fallback/disconnected): 3 passed
  ├ WebSocket adapter (active/fallback): 2 passed
  ├ DEX feed: 1 passed
  ├ Multi-feed scenarios: 2 passed (degraded mode, all disconnected)
```

### 핵심 개선
- feed_type 지정 시 명시적 우선순위 (hasattr 간섭 방지)
- Anomaly 감지: fallback 피드 1개 이상 → degraded_mode 경고
- WebSocket DISCONNECTED 상태 정확도 개선

## 다음 단계
- Health check 통합: data-agent 초기화 시 자동 feed 등록
- Monitoring으로 health report 주기적 집계
- Alert 시스템과 연동 (disconnected → alert)
