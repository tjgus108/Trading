# Current Cycle Briefing

_Cycle 297 완료 — 2026-06-11_
_카테고리: B(리스크) + D(ML) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **B(리스크)**: apply_wfe() 불일치 수정 + rvol_buy_sell 조정
   - `src/backtest/engine.py`: IS<-1.0+OOS>1.5 WFE=0.5 케이스 추가 (RollingOOSValidator 동기화)
   - `paper_simulation.py`: rvol_buy_sell 1.3→1.2 → relative_volume trades 15→17, 1/8 PASS

2. **D(ML)**: n_bins=3 실험 → 역효과 확인 → 복원
   - `src/strategy/price_cluster.py`에 n_bins 파라미터 추가됨 (코드 유지)
   - n_bins=3: Sharpe -2.78 (실패) → PAPER_SIM에서 제거, bounce_pct=0.015만 유지

3. **F(리서치)**: bull_only=True 실험 → 역효과 확인 → 복원
   - `src/strategy/momentum_quality.py`에 bull_only 파라미터 추가됨 (코드 유지)
   - bull_only=True: Sharpe 1.82→1.60 (실패) → PAPER_SIM에서 제거

### 시뮬레이션 결과

- Paper Sim BTC 4h: 0/22 PASS
  - price_cluster score=70.8, Sharpe=3.63 (복구)
  - relative_volume score=61.8, trades=17, **1/8 PASS** (첫 일관성 달성)
  - order_flow_imbalance_v2 **3/8 PASS** (MC=0.10 효과)
- Bundle OOS BTC 4h: **2/5 PASS** (cmf, supertrend_multi)
- 테스트: **8392 passed**

### 다음 사이클 (298) 방향

- 298 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)**
- C: price_cluster bounce_pct=0.02 시도 (trades 11→15 목표)
- B: relative_volume 추가 조정 또는 volatility_cluster 파라미터 검토
- F: order_flow_imbalance_v2 3/8→4/8 PASS 달성 전략 분석
