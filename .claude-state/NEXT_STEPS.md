# Cycle 49 - Category C: Data & Infrastructure 완료

## [2026-04-11] Cycle 49 — NewsMonitor 중복 감지 추가

### 작업 완료
- `src/data/news.py` 중복 감지 로직 추가
  - `_get_title_hash(title)`: MD5 기반 제목 hash (대소문자/공백 정규화)
  - `_is_duplicate(title_hash)`: 시간 윈도우 내 중복 확인
  - `_cleanup_old_hashes(now)`: 윈도우 외 오래된 hash 제거
  - `title_hash` 필드를 NewsEvent에 추가
  - `duplicate_window_hours` 파라미터 (기본 24시간)

- `tests/test_news_duplicate.py` 신규 생성 (7개 테스트)
  - title_hash 대소문자/공백 정규화
  - 동일/다른 헤드라인 중복 감지
  - 윈도우 외 만료 시간 처리
  - hash 정합성

### 파일 변경
- `src/data/news.py`: 중복 감지 로직 추가 (~290줄)
- `tests/test_news_duplicate.py`: 신규 생성 (7개 테스트)

### 테스트 결과
- tests/test_news_duplicate.py: 7/7 PASS ✓

---

# Cycle 48 - Category A: Quality Assurance — Test Fixtures 공통화 완료

## [2026-04-11] Cycle 48 — conftest.py 생성 및 테스트 Fixture 공통화

### 작업 완료
- `tests/conftest.py` 신규 생성 (170줄)
  - `sample_df` fixture: 기본 DataFrame (open, high, low, close, volume)
  - `sample_df_with_ema` fixture: EMA20, EMA50 지표 포함
  - `_make_df()` helper: ATR14, RSI14, Donchian, VWAP 지표 자동 생성
- 기존 테스트 호환성 100% 유지 (로컬 `_make_df` 함수들 그대로 유지)
- 향후 신규 테스트 작성 시 conftest 활용 권장

### 파일 변경
- `tests/conftest.py`: 신규 생성 (공통 fixture 제공)

### 테스트 결과
- tests/test_strategy.py: 5/5 PASS ✓
- tests/test_momentum_mean_rev.py: 16/16 PASS ✓
- tests/test_velocity_entry.py: 16/16 PASS ✓

---

