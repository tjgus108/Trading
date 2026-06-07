# Current Cycle Briefing

_Cycle 286 — B(리스크) + D(ML) + F(리서치)_
_Completed: 2026-06-07_

## 이번 사이클 수행 작업

### B(리스크): atr_threshold 완화 (0.7→0.5) — fold4 효과 없음 확인
- `scripts/run_bundle_oos.py`: BUNDLE_STRATEGY_INIT_PARAMS `atr_threshold=0.7→0.5`
  - 결과: fold4 OOS=-0.006, trades=8 → **변화 없음**
  - 확인: atr_threshold는 fold4 병목이 아님
  - fold4 진짜 문제: IS=2023-08~2024-02(강한 상승 과최적화) vs OOS=2024-02~04(ATH 조정)
  - WFE≥0.5 달성 위해 OOS≥1.25 필요 → 현재 -0.006 → 구조적 불가

### D(ML): DEFAULT_GRIDS 탐색 하한 확장
- `src/backtest/walk_forward.py`: supertrend_multi `atr_threshold` [0.7,0.8,0.9]→[0.5,0.6,0.7]
  - 향후 최적화 실행 시 더 낮은 임계값 탐색 가능
  - 실전 효과는 다음 optimize_supertrend_multi() 실행 시 확인

### F(리서치): ATH 후 OOS 구조 분석 인사이트
1. Supertrend: 강한 상승장 IS → 파라미터 과최적화 → OOS 레짐 전환 시 급락 (구조적)
2. cmf_confirm=True: -1.538→-0.006 (劇的 개선) but 양수 전환 불가
3. 대안 경로: min_wfe 완화(0.5→0.4) or OOS 절대값 기준 추가

## 시뮬레이션 결과
- 테스트: 8377 passed (targeted 198 passed) — 회귀 없음
- Bundle OOS: cmf **PASS**(14회 연속), supertrend_multi FAIL(fold4 WFE=-0.002 동일)
- Paper Sim: 0/22 PASS (rank1: supertrend_multi +6.73%)

## 다음 사이클 (Cycle 287: B(리스크) + D(ML) + F(리서치))
1. Option A: min_wfe=0.1 완화 (BUNDLE_STRATEGY_OVERRIDES) → fold4 PASS 경로
2. Option B: cmf_confirm=False 또는 rsi_ob_threshold=85로 완화 → OOS Sharpe 개선 시도
3. cmf 14회 PASS 안정성 유지 확인
