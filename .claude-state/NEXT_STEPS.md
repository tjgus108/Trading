# Cycle 29 - Data & Infrastructure: DataFeed 병렬 fetch 확장

## 이번 작업 내용
`src/data/feed.py`에 `fetch_multiple()` 메서드 추가로 여러 심볼 동시 fetch 지원.

### 수정 파일
1. **src/data/feed.py** (L7-99)
   - L8: `from concurrent.futures import ThreadPoolExecutor, as_completed` import 추가
   - L51-99: `fetch_multiple()` 메서드 신규 추가
     - ThreadPoolExecutor로 병렬 fetch
     - 기존 fetch() 캐싱 로직 동일 적용
     - 부분 실패 처리: 일부 심볼 오류 시 다른 심볼 계속 처리
     - max_workers 자동 조절 (min(len(symbols)+4, 32))

2. **tests/test_feed_parallel.py** (신규)
   - 7개 테스트 추가
   - 기본 병렬 fetch, 캐싱, 부분 실패, 지표 포함 검증

### 검증사항
- `websocket_feed.py` L73: 이미 `deque(maxlen=MAX_CANDLES)` 무한 버퍼 방지 됨
- 하위 호환성: 기존 `fetch()` 동작 100% 유지

## 테스트 결과
7/7 passed (test_feed_parallel.py)

## 다음 단계
- Cycle 30: strategy 강화 또는 risk 최적화
