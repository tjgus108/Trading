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
