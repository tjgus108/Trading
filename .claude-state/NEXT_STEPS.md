# Next Steps

_Last updated: 2026-06-01 (Cycle 259 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251~259

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 255 | A+C+F | GARCH CSV 생성, 0-trade score 버그 수정 |
| 256 | B+D+F | atr_tp 3.0→3.5, mom_quality_score 피처, **SOL 8/22 PASS** |
| 257 | B+D+F | HIGH conf 1.5→1.2, REGIME 피처, **ETH 5/22 PASS** |
| 258 | C+B+F | ETH/SOL GARCH CSV, HIGH conf 1.2→1.35 |
| 259 | D+E+F | **GARCH OU 평균회귀**, `--symbols`/`--csv-dir` 옵션, Bundle OOS CSV |

### 🎯 Cycle 260 작업 방향 (260 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): ETH 8-window 일관성 분석
- Cycle 259 ETH: momentum_quality Sharpe 1.30, volatility_cluster 1.31 — PASS 기준 돌파
- 그러나 8-window consistency 50% 미달 (몇 window에서 PF <1.5 또는 MDD >20%)
- 할 일: `PAPER_SIMULATION_RESULTS.json` ETH 데이터에서 어느 window에서 실패하는지 분석
  - 실패 window의 공통점 파악 (레짐? 변동성 스파이크?)
  - OU anchor 조정 또는 ou_theta 미세 튜닝 검토

#### C(데이터): GARCH OU 파라미터 튜닝
- 현재 ETH: ou_theta=0.003, anchor_mult=2.5 → 최종 가격 3708 (적정)
- 그러나 max 가격이 11655로 아직 높음 (price_max_mult=5.0 = 6000 초과)
  - anchor_mult를 2.0으로 낮추거나 ou_theta를 0.005로 높이는 실험
  - 목표: ETH max < 6000, 또는 max drawdown < 60%
- SOL: 이미 완벽 (12~247 범위) — 변경 불필요

#### F(리서치): CMF 레짐 의존성 분석
- Bundle OOS (BTC CSV): CMF avg OOS Sharpe 2.508 but std=1.888
  - Failed folds [0, 2, 3] vs Passed [1, 4]
  - 실패 fold의 시장 특성 vs 성공 fold 비교 → 레짐 조건 파악
  - CMF가 어떤 레짐에서 실패하는지 이해

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터만 사용 가능)
- BTC CSV: 실 binance 데이터 사용 가능 → Bundle OOS에 활용
- ETH/SOL: GARCH OU CSV 사용 (1196→3708, 15→99 범위)

### 핵심 메트릭 (Cycle 259)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: price_cluster sharpe=0.40, supertrend_multi 0.43)
- Paper Sim ETH: **0/22** (top: momentum_quality **Sharpe 1.30**, volatility_cluster 1.31)
  - Cycle 258 대비 개선: OU fix로 극단 드리프트 해소
- Paper Sim SOL: **0/22** (top: htf_ema Sharpe 0.51)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (CMF 93.6점, OOS Sharpe 2.508 but std 1.888>1.5)

### 주요 코드 변경 이력 (Cycle 259)
1. `scripts/generate_garch_csv.py` — OU 평균회귀 추가 (ou_theta, ou_anchor_mult, price_max/min_mult)
2. `scripts/paper_simulation.py` — `--symbols` 인자 추가 (심볼별 병렬 실행)
3. `scripts/run_bundle_oos.py` — `load_csv_and_resample()` + `--csv-dir` 인자 추가
