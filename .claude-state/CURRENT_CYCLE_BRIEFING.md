======================================================================
🔄 CYCLE 184 — 2026-05-20
======================================================================

## 이번 사이클 배정 카테고리 (184 mod 5 = 4)
- D(ML): WalkForward factory 버그 수정 + OOS std 필터
- E(실행): 거래 0건 전략 파라미터 완화
- F(리서치): IS Sharpe 기준 재검토

======================================================================
## 완료된 작업
======================================================================

### D(ML) — Walk-Forward factory 버그 수정
- EmaCrossStrategy: __init__(fast_span=20, slow_span=50) + _get_ema_values() 동적 계산
  - 기본값 + 컬럼 존재 시 pre-computed 사용 (완전 하위 호환)
  - 다른 params 시 close 가격에서 EWM 동적 계산
- DonchianBreakoutStrategy: __init__(channel_period=20) + _get_channel_values() 동적 계산
  - 기본값 + 컬럼 존재 시 pre-computed, 아닐 시 rolling(period).max/min
- optimize_ema_cross(): factory(params) → EmaCrossStrategy(fast_span, slow_span)
- optimize_donchian(): factory(params) → DonchianBreakoutStrategy(channel_period)
- IS 그리드 서치가 실제로 다른 파라미터 조합을 테스트하게 됨 ✅

### D(ML) — OOS Sharpe std 필터 (RollingOOSValidator)
- BundleOOSResult.oos_sharpe_std 필드 추가 (field 기본값 0.0)
- RollingOOSValidator.OOS_SHARPE_STD_MAX = 1.5
- validate() 끝에서 std > 1.5이면 all_passed=False + fail_reason 추가
- bundle_oos summary에 oos_sharpe_std 표시

### E(실행) — 파라미터 완화
- volume_breakout: _ATR_LOW 0.3→0.1, _ATR_HIGH 5.0→10.0
- dema_cross: 거리 필터 1.0%→0.5%
- price_cluster: _BOUNCE_THRESHOLD 0.002→0.005
- tests/test_volume_breakout.py: 경계값 테스트 업데이트

### 테스트
- 7582 passed, 17 skipped (all passing)

======================================================================
## 시뮬레이션 결과 (Synthetic data — Bybit SSL 차단)
======================================================================

paper_simulation (1h, BTC, 22 strategies, 8 windows): 0/22 PASS
bundle_oos (4h, 5 strategies, 9 folds, dry-run): 0/5 PASS
  - OOS Sharpe std 필터 동작 확인: 5/5 전략 std 3.16~6.15 > 1.5
⚠️ 합성 데이터 결과. 실제 Bybit 데이터로 재검증 필요.

======================================================================
## 다음 사이클 (185)
======================================================================
185 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)
최우선: IS Sharpe >= 2.5 subset 재검증 + 합성 데이터 현실성 개선
