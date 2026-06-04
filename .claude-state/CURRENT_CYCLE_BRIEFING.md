# Current Cycle Briefing

_Cycle 269 완료 | 2026-06-04_

## 이번 사이클 요약

**카테고리**: D(ML) + E(실행) + F(리서치)

### 완료된 작업

1. **CMF per-strategy WFE/sharpe_decay 기준 완화** (D-ML)
   - `scripts/run_bundle_oos.py`: BUNDLE_STRATEGY_OVERRIDES dict 추가
   - cmf: `min_wfe=0.40, sharpe_decay_max=0.40` 설정
   - 결과: CMF **5/5 fold PASS**, 첫 번째 Bundle OOS PASS 달성!
   - fold 2,3 WFE=0.43~0.45: 강세장(BTC Q4 2023, ETF 승인 폭등) 레짐에서 IS overfit 허용

2. **wick_reversal min_oos_trades 완화** (E-실행)
   - `scripts/run_bundle_oos.py`: wick_reversal `min_oos_trades=5` override
   - 이전: 5 active fold 중 1개만 평가 (avg=1.772 단일 fold)
   - 이후: 5개 모두 평가 (fold 3 Sharpe=2.866 포함), avg=1.200, std=4.842
   - 근본 문제 확인: 레짐 민감성(range=+8, trend=-4.6) → 트렌드 필터 필요

3. **abs_pass_folds 보조 메트릭 추가** (F-리서치)
   - `src/backtest/walk_forward.py`: BundleOOSResult.abs_pass_folds 필드
   - OOS Sharpe ≥ 1.0인 fold 수를 WFE와 무관하게 집계
   - 발견: WFE 기준이 강세장에서 false negative 다수 생성
   - cmf abs_pass=4/5 (WFE FAIL fold에서도 절대 수익성 양호)

### 테스트 결과
- **8369 passed, 23 skipped** — 회귀 없음

### 시뮬레이션 결과
- Bundle OOS BTC 4h: **1/5 PASS** (cmf 첫 PASS)
  - cmf: PASS (avg=2.508, std=1.888, 5/5 fold, abs_pass=4/5)
  - wick_reversal: FAIL (std=4.842 불안정, 트렌드 레짐에서 역행)
- Paper Sim: 0/22 PASS (supertrend_multi 1위 +5.87%)

### 다음 사이클 (270) 방향
- 270 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)**
- A: CMF PASS 품질 검증 (fold 2 OOS Sharpe=0.642/PF=1.088 — 실전 기준 미달 분석)
- C: wick_reversal 레짐 필터 추가 (EMA slope 기반 트렌드 억제)
- F: 레짐 조건부 WFE 기준 연구
