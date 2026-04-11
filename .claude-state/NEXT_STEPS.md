# Next Steps

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

