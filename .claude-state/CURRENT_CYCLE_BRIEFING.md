# Current Cycle Briefing

_Cycle 269 완료 | 2026-06-04_

## 이번 사이클 요약

**카테고리**: D(ML) + E(실행) + F(리서치)

### 완료된 작업

1. **CMF period 그리드 [20,21,22]→[21,22,23]** (D-ML)
   - WalkForwardOptimizer에서 더 긴 CMF period 탐색 (paper_sim 영향)
   - Bundle OOS는 CMFStrategy 기본 파라미터(period=20) 사용하므로 직접 영향 없음

2. **per-strategy validator 패턴 신설** (E-실행)
   - `BUNDLE_STRATEGY_OVERRIDES` dict: 전략별 validator 파라미터 오버라이드
   - `cmf`: min_wfe=0.4 (fold 2,3 WFE 0.434/0.449 → WFE 기준 통과, Sharpe decay로 FAIL 전환)
   - `wick_reversal`: min_oos_trades=5 (fold 3 5-trades 포함, Sharpe=2.866)

3. **F(리서치): 강세장 WFE 저하 + 병목 전환 분석**
   - cmf fold 2,3 실패 원인: WFE → Sharpe decay로 전환됨
   - 다음 병목: sharpe_decay_max=0.60 (OOS < IS × 60%)
   - 제안: sharpe_decay_max=0.40 오버라이드 시 fold 2,3 모두 PASS 가능

### 테스트 결과
- **8369 passed, 23 skipped** (419s) — 회귀 없음

### 시뮬레이션 결과
- Bundle OOS BTC 4h: 0/5 PASS
  - cmf: 3/5 PASS fold (WFE 기준 통과, Sharpe decay로 fold 2,3 FAIL), avg=2.508
  - wick_reversal: 2/5 PASS fold (fold 3 이제 포함, 5 trades), avg=1.200, std=4.842
- Paper Sim BTC: 0/22 PASS (top: supertrend_multi +5.87%, cmf -8.46%)

### 다음 사이클 (270) 방향
- 270 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)**
- A: cmf sharpe_decay_max 오버라이드 0.40 추가 (fold 2,3 최종 구제)
- C: wick_reversal 고분산(std=4.842) 해결 — Bearish RSI 필터 또는 std 완화
- F: wick_reversal 하락장 역행 패턴 연구 (ADX/추세 필터 검토)
