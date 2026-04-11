# Cycle 50 - Category D: ML & Signals — LLM retry wrapper 완료

## [2026-04-11] Cycle 50 — LLMAnalyst + Ensemble retry wrapper

### 작업 완료
- `src/alpha/llm_analyst.py`: `_with_retry()` 추가, `analyze_signal`에 적용 (3회, backoff 0.5/1.0s)
- `src/alpha/ensemble.py`: 동일 `_with_retry()` 추가, `_ask_claude`/`_ask_openai`에 적용
- `tests/test_llm_analyst.py`: `TestWithRetry` 클래스 4개 테스트 추가

### 테스트 결과
- tests/test_llm_analyst.py: 17/17 PASS

---

# Cycle 50 - Category F: Research — 50 사이클 마일스톤

## [2026-04-11] Cycle 50 — Top 3 Successful Bots 2025
- **CryptoRobotics**: 공개 성과 테이블. 상위 봇 월 수익률 60~266%. 신호 기반 멀티 전략.
- **Stoic**: 시장 중립 Meta 전략 ~45% APY, 헤지 캐리 Fixed Income 10~20% APY. 검증된 실적.
- **Pionex**: 월 거래량 $60B, 사용자 500만. Grid/DCA/Arbitrage 내장. 연 15~50% 차익 봇.
- 공통 키 특징: 24/7 자동화 + 리스크 관리 + 다중 전략 조합 + 실적 공개 투명성.

---

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

