# Current Cycle Briefing

_Cycle 340 | 2026-06-21 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): IS/OOS 레짐 불일치 진단 기능 추가

`scripts/paper_simulation.py` 개선:
1. `evaluate_strategy_walk_forward()`: 각 윈도우에 IS end-state 레짐 + OOS dominant regime 추가
   - IS regime: `_reg_diag.detect(train_df).value` (단일 호출)
   - OOS dominant regime: `detect_series(eval_df).iloc[-len(test_df):].mode()[0].value`
2. verbose-windows 출력에 `IS_Reg | OOS_Reg | Match` 컬럼 추가
3. 레짐 불일치 카운트를 전략 헤더에 표시

### C(데이터): 데이터 현황 확인

- BTC 1h CSV: 12000행, 2023-01-01~2024-05-14 (499일), 4h.csv 없음 (리샘플로 처리)
- SSL 차단으로 외부 데이터 수집 불가 — 현재 데이터가 최적
- Bundle OOS: `--csv-dir data/historical` 필수 플래그 확인

### F(리서치): IS/OOS 레짐 진단 분석 (price_cluster, roc_ma_cross)

핵심 발견:
- **price_cluster**: OOS_dom=RANGING + mkt=sideways(W6)에서만 PASS — 순수 횡보장 전략
  - W1(IS=TREND_UP, OOS=TREND_UP, bull): Sharpe=-1.43 — 상승장에서도 실패
  - W5(RANGING/RANGING, sideways): Sharpe=0.99 — 0.01 차이로 FAIL, 근접
- **roc_ma_cross**: IS=TREND_UP 종료 시에만 PASS
  - W1(IS=TREND_UP, OOS=TREND_UP, bull): Sharpe=4.04 PASS
  - W2(IS=TREND_UP, OOS=RANGING, bull): Sharpe=3.84 PASS
  - IS가 RANGING인 W3~W8 전부 FAIL

## 시뮬레이션 결과

- Paper Sim BTC 1h: **0/20 PASS** (20사이클 연속)
  - rank1: price_cluster (Sharpe=0.87, 1/8)
  - rank2: roc_ma_cross (Sharpe=0.34, 2/8) ← Cycle339 -0.43→+0.34 (필터 롤백 확인!)
- Bundle OOS BTC 4h: **5/5 PASS** ✅

## 테스트

- pytest: **8425 passed, 23 skipped** (회귀 없음)
