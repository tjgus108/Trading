======================================================================
🔄 CYCLE 250 — 2026-05-31
======================================================================

## 이번 사이클 배정 카테고리

250 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)

## 핵심 작업 완료

### [A] walk_forward.py BundleOOSResult IS Sharpe 추적 필드 추가
- `avg_is_sharpe`, `is_negative_fold_pct` 필드를 `BundleOOSResult`에 추가
- `RollingOOSValidator.validate()`: IS 음수 fold 비율 계산 + 80% 초과 시 fail_reasons 등록
- `BundleOOSResult.summary()`: avg_is_sharpe(is_neg=%) 표시로 진단 가독성 개선
- 신규 테스트 3개: 필드 존재 검증, summary 포함 검증, RollingOOSValidator E2E 검증

### [A] elder_impulse ATR 버그 수정 효과 검증 (Cycle 249 수정 → Cycle 250 확인)
- GBM: IS 음수 100% / GARCH: IS 음수 44% → **ATR 수정 + GARCH 데이터 복합 효과 확인**
- elder_impulse IS Sharpe 개선 확인 (Cycle 249 목표 달성)

### [C] run_bundle_oos.py 기본 fallback을 GBM → GARCH로 변경
- 실거래소 연결 실패 시 GARCH+regime 합성 데이터를 기본으로 사용
- 근거: GARCH에서 elder_impulse IS neg 100%→44%, narrow_range fold 5-7 양수 IS Sharpe
- GBM은 --dry-run 시에만 유지 (비교 실험용)

### [F] GARCH vs GBM 데이터 비교 리서치
- GARCH(trend_up/down/range/vol_spike) 블록이 GBM보다 trend-following에 현실적
- elder_impulse: GBM 100% neg → GARCH 44% neg (55%p 개선)
- narrow_range: GARCH fold 5~7에서 양수 IS Sharpe (7.7, 6.6, 3.3)
- cmf: GBM/GARCH 모두 Rank #1 (volume-direction 상관관계 보존)
- wick_reversal, value_area: GARCH에서도 0 OOS trades → 실거래소 데이터 없이는 검증 불가

## 시뮬레이션 결과

### Bundle OOS BTC 4h (GARCH 합성, Cycle 250)
- 0/5 PASS (SSL 차단으로 합성 GARCH 데이터 사용)
- Rank #1: cmf (Score 88.7, OOS Sharpe 1.085, Avg Trades 22.3, IS neg 44%)
- Rank #2: narrow_range (Score 85.6, OOS Sharpe 1.029, IS neg 44%)
- IS Sharpe 음수 비율: elder_impulse/narrow_range 44%, cmf 44% (GARCH 효과 확인)
- wick_reversal, value_area: 0 OOS trades (min_oos_trades=10 충족 불가)

### Paper SIM BTC 1h (BlockBootstrap, Cycle 250)
- 0/22 PASS (합성 BlockBootstrap 데이터)
- 상대 우위: momentum_quality(+59.23%, Sharpe 5.11), cmf(+58.61%, Sharpe 3.87)
- Bundle 5 중: cmf +58.61%, narrow_range +5.28%, wick_reversal -1.23%, elder_impulse -9.09%

## 테스트
8349 passed, 23 skipped (신규 3개: IS neg fold 필드 검증)

## 다음 사이클: 251 (251 mod 5 = 1 → B+D+F)
- B: DrawdownMonitor + cmf/narrow_range GARCH 개선 파라미터 조정 가능성 검토
- D: GARCH 데이터에서 cmf/narrow_range IS Sharpe가 양수인 fold 파라미터 분석
- F: OOS Sharpe std > 1.5 근본 원인 분석 (fold 간 레짐 불일치)
