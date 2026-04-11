# Next Steps

## Cycle 18 - API Key Permission 검증 ✅ COMPLETED

**Task:** startup 시 API Key 출금 권한 체크 기능 추가

**Changes:**
1. `src/exchange/connector.py` line 35 — `connect()` 끝에 `self.check_api_permissions()` 호출 추가
2. `src/exchange/connector.py` lines 37-65 — `check_api_permissions()` 메서드 추가
   - 출금 권한 있으면 → `CRITICAL` 로그 (SECURITY WARNING)
   - 출금 권한 없으면 → `INFO` 로그 (passed)
   - `ccxt.NotSupported` 시 → `WARNING` 로그 + 빈 dict 반환
3. `tests/test_api_key_permissions.py` — 4개 테스트 신규 작성

**Test Results:** 4/4 passed ✅

---

## Cycle 18 - Category A: Quality Assurance ✅ COMPLETED

**Task:** walk_forward.py 테스트 보강 (경계 조건)

**Changes:**
1. `tests/test_walk_forward.py` lines 191-237 — 3개 테스트 추가

**Test Coverage:**
- WalkForwardValidator: 10 → 11개 테스트
- WalkForwardOptimizer: 0 → 2개 테스트
- **Total: 13/13 passed ✅**

---

## Cycle 17 - Category B: Risk Management ✅ COMPLETED

**Task:** Order Jitter — 봇 예측 가능성 차단 (AMM 착취 대응)

**Changes:**
1. `src/risk/manager.py` lines 107, 114 — jitter_pct 파라미터 추가
2. `src/risk/manager.py` lines 213-218 — jitter 적용 로직
3. `tests/test_risk_manager.py` lines 210-247 — 4개 테스트 추가

**Test Results:** 31/31 passed ✅

---

## Next Opportunities (Future Cycles)

### Security
- check_api_permissions() 결과를 config 경고 파일로도 기록 (선택)
- API Key rotation reminder (30일 주기) 추가

### Walk-Forward Validation
- Multi-window optimization tests (IS/OOS Sharpe ratio overfitting)

### Real Exchange Data Backtest
- Fetch 1+ year BTC-USDT from Binance
- Stress test 22 PASS strategies
