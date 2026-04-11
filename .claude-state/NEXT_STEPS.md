# Cycle 21 - QA: 테스트 속도 최적화

## 완료: 테스트 성능 최적화 (Option 2)

### 이번 작업 내용
`tests/test_orchestrator.py` — 외부 HTTP 호출 mocking으로 느린 테스트 가속

**주요 변경:**
1. **상위 병목 식별** 
   - `test_run_once_returns_pipeline_result` 4.97s → 0.57s (3.5배 개선)
   - 원인: SentimentFetcher.fetch() HTTP 재시도 (5초 타임아웃)

2. **Mock 패치 추가** (lines 121-133)
   - `SentimentFetcher.fetch()` mocking → SentimentData 반환
   - `OnchainFetcher.fetch()` mocking → 블록체인 API 호출 차단
   - 단위: patch 데코레이터 제거 → context manager 사용 (테스트 격리)

3. **전체 성능 개선**
   - 전체 테스트 스위트: 35.53s → 31.02s (13% 개선)
   - 전체 테스트 통과: 5927 passed, 27 skipped

### 변경 파일
- `tests/test_orchestrator.py` — lines 117-136

### 테스트 결과
```
tests/test_orchestrator.py::16 tests — 1.54s
전체: 5927 passed, 27 skipped in 31.02s
```

성능 비교:
- Before: 4.97s (상위 1위)
- After: 0.57s (상위 8위)
- 개선율: 3.5배

## 다음 단계
- Cycle 21 Category A 완료
- OrderFlow VPIN 성능 최적화 (Cycle 22 옵션)
