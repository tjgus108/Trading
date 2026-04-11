# Next Steps

## Cycle 18 - API Key Permission 검증 ✅ COMPLETED (2차 확인)

**Task:** check_api_permissions() 단위 테스트 추가 (기존 구현 검증)

**Confirmed:** `src/exchange/connector.py` lines 37-65 — 이미 구현 완료 상태
- `connect()` 끝에서 자동 호출 (line 35)
- 출금 권한 → CRITICAL 로그
- 미지원 거래소 → WARNING + 빈 dict

**New Tests:** `tests/test_connector.py` — 3개 신규 작성
1. `test_check_permissions_no_withdraw` — 정상 패스
2. `test_check_permissions_withdraw_enabled` — CRITICAL 로그 확인
3. `test_check_permissions_not_supported` — NotSupported 처리

**Test Results:** 3/3 passed ✅

---

## Cycle 18 - API Key Permission 검증 ✅ COMPLETED (1차)

**Task:** startup 시 API Key 출금 권한 체크 기능 추가

**Changes:**
1. `src/exchange/connector.py` line 35 — `connect()` 끝에 `self.check_api_permissions()` 호출 추가
2. `src/exchange/connector.py` lines 37-65 — `check_api_permissions()` 메서드 추가
3. `tests/test_api_key_permissions.py` — 4개 테스트 신규 작성

**Test Results:** 4/4 passed ✅

---

## Cycle 18 - Category A: Quality Assurance ✅ COMPLETED

**Changes:**
1. `tests/test_walk_forward.py` lines 191-237 — 3개 테스트 추가
**Total: 13/13 passed ✅**

---

## Cycle 17 - Category B: Risk Management ✅ COMPLETED

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
