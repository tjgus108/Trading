# Current Cycle Briefing

_Cycle 337 | 2026-06-20 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): MAX_HOLD=48 실험 → 즉시 복원

- `engine.py` MAX_HOLD_CANDLES 24→48 변경 후 Bundle OOS 4h 재실행:
  - **5/5 → 2/5 PASS (SEVERE REGRESSION)**
  - value_area: OOS Sharpe 3.069 → 0.090 (catastrophic!)
  - cmf: OOS Sharpe std 2.417 > 2.0 (불안정)
  - vwap_cross: OOS Sharpe std 2.676 > 2.0 (불안정)
- **즉시 MAX_HOLD=24 복원** → Bundle OOS 5/5 PASS 재확인
- **핵심 발견**: MAX_HOLD=48 at 4h = 8일 보유 (지나치게 길어 전략 구조 붕괴)
  - 1h: 48봉 = 2일 (OK, Cycle336 개별 실험에서 개선 확인)
  - 4h: 24봉 = 4일 (OK, 5/5 PASS 유지)
  - 4h: 48봉 = 8일 (NG, 즉시 복원 필요)
- **결론**: Cycle 338에서 engine.py에 TF별 MAX_HOLD dict 구현 필요

### D(ML): OFI buy_thresh=0.30 → 0.25 복원

- `scripts/paper_simulation.py` PAPER_SIM_STRATEGY_PARAMS:
  - `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` → `{"trend_span": 20}`
- 복원 이유:
  1. ETH 악화: rank15, Sharpe=-2.40 (Cycle 336 실험 결과)
  2. Cycle 300 전례: 동일 0.30 시도 → 역효과 후 복원 기록 있음
  3. BTC 개선(Sharpe -0.83→-0.64)이 멀티심볼 악화보다 작음
- Paper sim (이번 사이클): buy_thresh=0.30 상태로 실행됨 (시작 전 변경이어서)
  - OFI rank6: Sharpe=-0.70, PF=0.96, 67 trades (0.30 기준)
  - 다음 paper sim에서는 0.25(기본값)로 실행됨

### F(리서치): SL/TP 비율 분석 (ATR 기반)

- `engine.py` 현재: atr_multiplier_sl=1.5, atr_multiplier_tp=3.5 → R:R = **2.33:1**
- 이전 NEXT_STEPS "SL=5%, TP=2%" 설명은 **오류** — 실제는 ATR 기반 (고정% 아님)
- WR=38%에서 이론 PF = (0.38×2.33)/(0.62×1.0) = **1.43** (임계값 1.50에 0.07 차이)
- PF≥1.5 달성을 위한 최소 R:R = 2.45 (현재 2.33보다 0.12 부족)
- 실험 후보 (Cycle 338 F): atr_multiplier_tp=3.5→4.0 (R:R=2.67, 이론 PF=1.63)
  - MAX_HOLD TF-aware 구현 후 paper sim 결과 보고 결정

## 시뮬레이션 결과 (Cycle 337)

- **테스트**: 8425 passed, 23 skipped (회귀 없음)

- **Paper Sim BTC 1h (20전략, 8 windows, MAX_HOLD=24, OFI buy_thresh=0.30)**: **0/20 PASS** (17사이클 연속)
  - rank1: price_cluster (Sharpe=**0.90**, PF=1.21, 41 trades, 2/8) ← **이전 0.34 대비 대폭 개선!**
  - rank2: roc_ma_cross (Sharpe=0.25, PF=1.20, 36 trades, 2/8)
  - rank3: frama (Sharpe=0.33, PF=1.15, 40 trades, 1/8)
  - rank6: OFI v2 (Sharpe=-0.70, PF=0.96, 67 trades)
  - 주요 FAIL 원인: PF<1.5, Sharpe<1.0 (PASS 기준 0.1 이내 근접)

- **Paper Sim ETH 1h**: 0/20 PASS (rank1: volatility_cluster Sharpe=0.63)

- **Paper Sim SOL 1h**: 0/20 PASS (rank1: momentum_quality Sharpe=-0.37)

- **Bundle OOS BTC 4h (MAX_HOLD=24 복원)**: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (338 mod 5 = 3): C(데이터) + B(리스크) + F(리서치)

- **B(리스크)**: engine.py TF별 MAX_HOLD 구현 (1h:48봉, 4h:24봉)
  - `TF_MAX_HOLD = {"1h": 48, "4h": 24, "1d": 10}` dict 추가
  - `run()` 메서드에서 `max_hold = TF_MAX_HOLD.get(self.timeframe, MAX_HOLD_CANDLES)` 사용
  - 4h Bundle OOS 영향 없음 (TF_MAX_HOLD["4h"]=24 변경 없음)
- **C(데이터)**: price_cluster Sharpe 0.90 분석 (어느 window에서 강한지 확인)
  - PAPER_SIMULATION_RESULTS.csv로 window별 상세 분석
- **F(리서치)**: B 완료 후 paper sim 결과 보고 atr_multiplier_tp=4.0 실험 여부 결정
