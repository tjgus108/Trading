# Current Cycle Briefing

_Cycle 346 | 2026-06-22 | B(리스크) + D(ML)_

## 완료된 사이클: 346
**카테고리**: B(리스크) + D(ML)

### D(ML): per-strategy min_hold_bars 지원 추가

**작업**:
- `scripts/paper_simulation.py`에 `PAPER_SIM_MIN_HOLD_BARS: Dict[str, int] = {"roc_ma_cross": 4}` 추가
- `simulate_symbol()` 시그니처 확장: `per_strategy_engines: Optional[Dict[str, BacktestEngine]] = None`
- evaluation loop: `_eval_engine = (per_strategy_engines or {}).get(mod_name, engine)` 전략별 engine 선택
- `run_simulation()`에 PAPER_SIM_MIN_HOLD_BARS 기반 per-strategy engine 생성 블록 추가

**검증**:
- `[CONFIG] PAPER_SIM_MIN_HOLD_BARS active: roc_ma_cross=4` 출력 확인
- roc_ma_cross: Sharpe=0.99 (Cycle 345 MHB4 실험 재현) ✅
- price_cluster: Sharpe=0.87 (전역 min_hold_bars=0, 영향 없음) ✅

### B(리스크): roc_ma_cross PF 개선 탐색

**전략 분석**:
- 진입: ROC_MA 0 크로스 + ROC>_ROC_MIN_ABS + EMA50/200 필터
- W1(TREND_UP IS+OOS, bull): Sharpe=4.04 PASS — 강한 상승 모멘텀 구간
- W2(TREND_UP IS + RANGING OOS, bull): Sharpe=3.84 PASS — IS 확립 후 RANGING 유지
- W3-W8: RANGING/bear → 근본적 regime 불일치

**실험**: `_ROC_MIN_ABS` 0.3% → 0.5% (단독 실험)

| 지표 | Before (MHB4, ROC0.3%) | After (MHB4, ROC0.5%) | 변화 |
|------|----------------------|---------------------|------|
| Sharpe | 0.99 | **1.14** | +0.15 |
| PF | 1.34 | 1.37 | +0.03 |
| Trades | 34 | 33 | -1 |
| Consistency | 2/8 | 2/8 | 유지 |

창별 결과 (ROC0.5%):
- W1: Sharpe=4.30, PF=2.40 PASS ✅
- W2: Sharpe=3.81, PF=2.06 PASS ✅
- W3: Sharpe=0.84, PF=1.20 FAIL (Sharpe<1.0)
- W4: Sharpe=0.71, PF=1.17 FAIL
- W5: Sharpe=-2.10, PF=0.69 FAIL (bear 구간 근본 한계)
- W6: Sharpe=1.20, PF=1.29 FAIL (MC_p=0.259>0.1 통계 미달)
- W7: Sharpe=0.98, PF=1.22 FAIL (Sharpe 0.02 미달)
- W8: Sharpe=-0.62, PF=0.91 FAIL

**결론**: Sharpe+0.15 순개선. 2/8→4/8 PASS 불가 (RANGING/bear 창 regime 한계). 변경 유지.

## 시뮬레이션 결과

### Paper Simulation (1h, 8-fold, BTC/ETH/SOL)
- **PASS: 0/20** (BTC: 26연속)
- BTC Top: roc_ma_cross (Sharpe=1.14, 2/8), price_cluster (Sharpe=0.87, 1/8)
- ETH Top: price_action_momentum (0.23), volatility_cluster (0.82) — synthetic
- SOL Top: momentum_quality (-0.17), order_flow_imbalance_v2 (-0.37) — synthetic

### Bundle OOS (4h, BTC/USDT)
- **PASS: 5/5** ✅ (유지)
- #1 order_flow_imbalance_v2 (Score=62.0, OOS Sharpe=4.345)

## 테스트 결과

- **8432 passed, 0 failed** (변화 없음)

## 다음 사이클 (347) 방향

347 mod 5 = 2 → **C(데이터) + E(실행)**
