# Next Steps

## Cycle 13 - Category A: Quality Assurance ✅ COMPLETED

**Task:** 품질 감사 재실행 + 리포트 갱신

**Changes:**
1. `scripts/quality_audit.py` 재실행
   - 합성 데이터 생성 시 donchian_high, ema20, vwap 추가
   - 모든 348개 전략 에러 없이 정상 백테스트 (0% error rate)

2. `.claude-state/BACKTEST_REPORT.md` 갱신
   - PASS: 22개 (6.3%)
   - FAIL: 326개 (93.7%)
   - 에러: 0개 (이전 5개 → 완전 해결) ✅

**Key Metrics (PASS Strategies):**
- Sharpe: avg 4.79, median 4.77 (very strong)
- Max DD: avg 3.62%, median 3.40% (very stable)
- Profit Factor: avg 1.95, median 1.85 (safe margin)
- Win Rate: avg 53.1% (balanced)
- Return: avg 9.53%

**Failure Patterns:**
- Trade volume < 15: ~50 strategies (most common)
- Profit Factor < 1.5: ~100 strategies (economics fail)
- Zero trades generated: 15 strategies

**Test Results:** ✅ Quality audit completed, no regressions

---

## Previous Cycles (Reference)

### Cycle 12 - Category B: Risk Management ✅ COMPLETED
- Correlation Throttle 로직 이미 구현 확인
- Test helper bug fix: `_make_tracker_with_high_corr()` 신호 패턴 개선
- Result: 17/17 tests passed

### Cycle 12 - Category D: ML & Signals ✅ COMPLETED  
- Feature leakage: `_compute_labels()` 마지막 행 NaN 버그 수정
- Scaler leakage: LSTM fit on train only
- Tests: 28 passed (3 new leakage tests)

### Cycle 11 - Category C: Data & Infrastructure ✅ COMPLETED
- Look-ahead bias: All rolling/EMA shifted by 1 bar
- Result: 5849 tests passed

### Cycles 1, 3, 6, 8: Warning/audit/numpy/Sortino validation completed

---

## Cycle 14 Recommendations (Future)

### Option 1: Walk-Forward Validation (Priority)
- Implement 70/30 train/test split for 22 PASS strategies
- Add IS/OOS correlation test (overfitting detection)
- Location: `src/backtest/walk_forward.py` (new)
- Test in: `tests/test_walk_forward.py` (new)

### Option 2: Real Exchange Data Backtest
- Fetch 1+ year BTC-USDT historical from Binance API
- Stress test 22 PASS strategies
- Compare vs synthetic data results
- Location: `src/data/real_exchange_fetch.py`

### Option 3: Portfolio Correlation Analysis
- Analyze signal correlation across 22 PASS strategies
- Identify redundant pairs
- Build diversified portfolio
- Location: `src/analysis/strategy_correlation_detailed.py`

### Option 4: Monte Carlo Test Coverage
- `src/backtest/monte_carlo.py` Block Bootstrap tests
- Add confidence intervals
- Location: `tests/test_monte_carlo.py` (expand)

---

## Key Files
- Report: `/home/user/Trading/.claude-state/BACKTEST_REPORT.md`
- Results CSV: `/home/user/Trading/.claude-state/QUALITY_AUDIT.csv`
- Audit Script: `/home/user/Trading/scripts/quality_audit.py`

---

## Cycle 15 - Category D: ML & Signals - LLMAnalyst Robustness ✅ COMPLETED

**Task:** LLM API 실패 처리 강화 (타임아웃, 빈 응답, 예상 외 텍스트)

**Changes:**
1. `src/alpha/llm_analyst.py` lines 17, 82-91, 104-115
   - `_TIMEOUT_SECONDS = 15` 상수 추가
   - `messages.create()` 호출에 `timeout=_TIMEOUT_SECONDS` 적용 (analyze_signal, classify_news_risk 둘 다)
   - `response.content` 빈 리스트 guard 추가 (IndexError 방지)
   - 빈 문자열 반환 시 warning 로깅
   - 예외 로그에 `type(e).__name__` 포함 (디버깅 향상)
   - `classify_news_risk` 예상 외 텍스트 debug→warning 으로 격상

2. `tests/test_llm_analyst.py` (신규, 10개 테스트)
   - analyze_signal: 성공/API예외/빈content/빈텍스트/disabled 5케이스
   - classify_news_risk: 정상분류/API예외/빈content/예상외텍스트/disabled 5케이스

**Test Results:** 10/10 passed ✅

---

## Cycle 14 - Category B: Risk Management - VaR/CVaR 검증 ✅ COMPLETED

**Task:** portfolio_optimizer.py VaR/CVaR 정확도 검증 + 경계 조건 테스트

**Findings:**
- `_compute_var_cvar()`: historical simulation 방식, 손실 양수 반환 — 로직 정상
- cutoff_idx 경계(T=20, confidence=0.95 → cutoff=1): CVaR==VaR 허용 케이스 미검증
- 모든 수익률 양수 시 max(0,x) 처리로 VaR=0/CVaR=0 반환 — 미검증

**Changes:**
1. `tests/test_portfolio_optimizer.py` lines 182-204 — 경계 조건 테스트 2개 추가
   - `test_var_cvar_small_sample_boundary`: T=20 cutoff=1 경계 검증
   - `test_var_cvar_all_positive_returns`: 전 양수 수익률 VaR=0 검증

**Test Results:** 18/18 passed ✅

---

## Cycle 15 - Orchestrator Runtime Metrics: Implementation Shortfall 누적 추적 ✅ COMPLETED

**Task:** run_once() 실행 루프에서 Implementation Shortfall 누적 메트릭 추적 추가

**Changes:**
1. `src/orchestrator.py`
   - line 19: `from typing import List, Optional`
   - line 811: `self._impl_shortfall_samples: List[float] = []` 필드 추가
   - lines 913-924: `run_once()` 내 cycle_count 증가 직후, impl_shortfall_bps 발생 시 samples 누적 + avg 로깅 추가
     `[metrics] impl_shortfall cycle=N value=Xbps avg=Ybps n=Z`

2. `tests/test_orchestrator.py`
   - 기존 `test_impl_shortfall_calculated_on_fill` Signal/RiskResult 파라미터 버그 수정 (line 377~391)
   - `test_impl_shortfall_samples_accumulated` 신규 추가 (lines 415~462): 3 사이클 누적 후 len==3, avg 정확도 검증

**Test Results:** 16/16 passed ✅
