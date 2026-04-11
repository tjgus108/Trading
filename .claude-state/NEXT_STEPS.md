# Cycle 55 - Config Migration Helper 완료

## [2026-04-11] Cycle 55 — migrate_config 헬퍼 추가

### 작업
- `src/config.py`: `migrate_config(raw)` 함수 추가 (line 187)
  - 구버전 키 `risk.stop_loss` → `risk.stop_loss_atr_multiplier` 자동 변환
  - 구버전 키 `risk.take_profit` → `risk.take_profit_atr_multiplier` 자동 변환
  - 누락 risk/trading 필드에 기본값 자동 채움 + UserWarning 발생
  - `load_config()`에서 yaml 파싱 직후 호출
  - `rsk.get("stop_loss", ...)` → `rsk.get("stop_loss_atr_multiplier", ...)` 수정

### 테스트 추가
- `tests/test_config.py`:
  - `test_migrate_config_renames_old_keys`: 구버전 키 변환 + 경고 확인
  - `test_migrate_config_fills_missing_defaults`: 누락 필드 기본값 채움 확인

### 테스트 결과
- tests/test_config.py: 10/10 PASS

---

# Cycle 55 - Category D: ML & Signals 완료

## [2026-04-11] Cycle 55 — WalkForwardValidator 경계 조건 테스트 추가

### 확인 사항
- `src/backtest/walk_forward.py`: WalkForwardValidator.validate()가 BacktestEngine.run()을 올바르게 호출 (fee_rate, slippage_pct 전달 확인)
- 경계 조건 버그 없음 — 데이터 부족 시 ValueError, 최솟값 데이터 시 윈도우 1개 정상 생성

### 테스트 추가
- `tests/test_backtest.py`:
  - `test_walk_forward_validator_raises_on_insufficient_data`: 100봉 < train(200)+test(50) → ValueError
  - `test_walk_forward_validator_exact_minimum_data`: 250봉 정확히 최솟값 → windows=1, 메타데이터 검증

### 테스트 결과
- tests/test_backtest.py: 8/8 PASS

---

# Cycle 54 - Category B: Risk Management 완료

## [2026-04-11] Cycle 54 — Portfolio Optimizer Sanity Check 강화

### 버그 수정
- `src/risk/portfolio_optimizer.py` `_apply_constraints()`:
  - NaN/inf 입력 방어 추가 (시작 시 `np.isfinite` 체크 → equal_weight fallback)
  - 500회 루프에서 수렴 성공 시 즉시 break 후 후처리로 진입하도록 개선
  - 최종 반환 전 `clip(w, 0, None) / sum` 으로 합=1, 음수=0 강제 보장

### 테스트 추가 (수치 불안정 시나리오)
- `tests/test_portfolio_optimizer.py`:
  - `test_nan_weights_to_apply_constraints_returns_equal_weight`: NaN 입력 → equal_weight
  - `test_inf_weights_to_apply_constraints_returns_equal_weight`: inf 입력 → equal_weight

### 테스트 결과
- tests/test_portfolio_optimizer.py: 23/23 PASS ✓

---

# Cycle 54 - Category C: DataFeed rate limit 감지 완료

## [2026-04-11] Cycle 54 — DataFeed rate limit 감지 + backoff

### 작업 완료
- `src/data/feed.py`: RateLimitExceeded 전용 처리 추가
  - `_is_rate_limit_error()`: ccxt.RateLimitExceeded 감지
  - `_backoff_with_rate_limit()`: rate limit은 긴 backoff (2 + attempt*2초), 다른 transient는 짧은 backoff (0.5*attempt초)
  - `_fetch_with_retry()` line 139: 동적 backoff 호출로 변경

### 파일 변경
- `src/data/feed.py`: +3개 함수 (46-70줄)
- `tests/test_rate_limit_backoff.py`: 신규 테스트 파일 (6개 테스트)

### 테스트 결과
- tests/test_rate_limit_backoff.py: 6/6 PASS ✓
  - test_is_rate_limit_error (감지 로직)
  - test_backoff_with_rate_limit_long_wait (첫 시도: 4초)
  - test_backoff_with_rate_limit_increasing (증가형: 4s, 6s, 8s)
  - test_backoff_with_other_transient_error (다른 에러: 0.5s*attempt)
  - test_fetch_with_rate_limit_retry (재시도 성공)
  - test_fetch_with_rate_limit_exhausted (재시도 실패)
- tests/test_feed_parallel.py::TestErrorClassification (회귀): 1/1 PASS ✓

---

# Cycle 54 - Category F: Research — ETF Flows as Signal

(이전 항목...)

---
