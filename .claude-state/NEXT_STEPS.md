# Next Steps

## Cycle 17 - Category B: Risk Management ✅ COMPLETED

**Task:** Order Jitter — 봇 예측 가능성 차단 (AMM 착취 대응)

**Changes:**
1. `src/risk/manager.py` line 9 — `import random` 추가
2. `src/risk/manager.py` lines 107, 114 — `__init__`에 `jitter_pct: float = 0.0` 파라미터 추가 (상한 5% 클램프)
3. `src/risk/manager.py` lines 213-218 — max_size 클램프 후 `random.uniform(-jitter_pct, jitter_pct)` 적용
4. `tests/test_risk_manager.py` lines 210-247 — 4개 테스트 추가
   - `test_jitter_varies_position_size`: 30회 호출 시 2개 이상 다른 값
   - `test_jitter_within_bounds`: 50회 호출 모두 ±5% 범위 내
   - `test_jitter_zero_is_deterministic`: jitter=0이면 항상 동일값
   - `test_jitter_pct_clamped_at_five_percent`: 0.99 입력 → 0.05 클램프

**Test Results:** 31/31 passed ✅

---

## Cycle 17 - Category D: ML & Signals ✅ COMPLETED

**Task:** MultiLLMEnsemble 병렬 호출 (레이턴시 최적화)

**Changes:**
1. `src/alpha/ensemble.py` line 1 — `concurrent.futures.ThreadPoolExecutor` import 추가
2. `src/alpha/ensemble.py` lines 148-162 — `_ask_parallel()` 메서드 추가 (Claude + OpenAI 병렬)
3. `src/alpha/ensemble.py` line 127 — `analyze()` 내 순차 호출 → `_ask_parallel()` 단일 호출로 교체
4. `tests/test_phase_d.py` — `test_ask_parallel_both_na_without_clients`, `test_ask_parallel_uses_stub` 2개 추가

**Test Results:** 13/13 passed ✅

---

## Cycle 16 - Category A: Quality Assurance ✅ COMPLETED

**Task:** pipeline/runner.py 테스트 커버리지 보강

**Changes:**
1. `tests/test_pipeline_specialist.py` lines 179-247 — 5개 새 테스트 추가
   - `test_pipeline_risk_blocked`: RiskStatus.BLOCKED 경로 검증
   - `test_pipeline_execution_fails`: Execution 예외 처리 검증 
   - `test_pipeline_ensemble_conflict_llm`: MultiLLMEnsemble conflict → HOLD 전환 경로
   - `test_pipeline_kelly_sizing`: Kelly position sizer 활성화 경로 (H1)
   - `test_pipeline_vol_targeting`: Vol-targeted sizing 활성화 경로 (I3)

**Coverage Improvements:**
- ✅ Risk block path (line 236-240): 신호 발생 시 risk BLOCKED로 반환
- ✅ Execution failure path (line 344-348): 예외 발생 시 ERROR 상태
- ✅ Ensemble conflict path (line 151-166): conflicts_with() 반환 시 HOLD 전환
- ✅ Kelly/Vol-targeting paths (line 243-270): 추가 position_size 조정

**Test Results:** 10/10 passed ✅
- 기존 5개 테스트 계속 유지
- 새로운 5개 테스트 모두 통과

---

## Previous Cycles (Reference)

### Cycle 15 - Orchestrator Runtime Metrics ✅ COMPLETED
- Implementation Shortfall 누적 메트릭 추적

### Cycle 15 - Category D: ML & Signals - LLMAnalyst Robustness ✅ COMPLETED
- LLM API 실패 처리 강화

### Cycle 14 - Category B: Risk Management - VaR/CVaR 검증 ✅ COMPLETED
- portfolio_optimizer.py VaR/CVaR 경계 조건 테스트

### Cycle 13 - Category A: Quality Assurance ✅ COMPLETED
- 품질 감사 재실행 + 리포트 갱신 (348개 전략, 에러율 0%)

### Cycles 1-12: Warning/audit/numpy/Sortino/look-ahead bias/feature leakage validation

---

## Key Files
- Modified: `/home/user/Trading/tests/test_pipeline_specialist.py` (lines 179-247)
- Reference: `/home/user/Trading/src/pipeline/runner.py`
- Report: `/home/user/Trading/.claude-state/BACKTEST_REPORT.md`

---

## Next Opportunities (Future Cycles)

### Walk-Forward Validation (Priority)
- 70/30 train/test split for 22 PASS strategies
- IS/OOS correlation test (overfitting detection)
- Location: `src/backtest/walk_forward.py`

### Real Exchange Data Backtest
- Fetch 1+ year BTC-USDT from Binance
- Stress test 22 PASS strategies
- Compare vs synthetic data

### Portfolio Correlation Analysis
- Signal correlation across 22 PASS strategies
- Identify redundant pairs
- Build diversified portfolio

