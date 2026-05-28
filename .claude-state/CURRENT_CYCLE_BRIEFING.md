======================================================================
🔄 CYCLE 235 — 2026-05-28
======================================================================

## 이번 사이클 배정 카테고리

### [A] Quality Assurance — MC Permutation Test 버그 수정
- **근본 원인 발견 및 수정**:
  - `src/backtest/engine.py` `_mc_permutation_test`:
    - **버그**: equity-curve Sharpe(candle 단위)를 임계값으로 사용, trade PnL로 permuted Sharpe 계산
    - 수식: 111 trades → perm_sharpe ~ N(0, sqrt(8760/111)) ≈ N(0, 8.9)
    - P(Z ≥ 4.22/8.9) ≈ 0.317 — 관측값 0.31~0.34와 정확히 일치
    - **수정**: trade-based original Sharpe 내부 계산 후 비교 (동일 계산 기준)
  - **효과**: 모든 심볼 PASS 0 → BTC 7, ETH 11, SOL 4

### [C] Data — BlockBootstrap block_size 확대
- `scripts/paper_simulation.py`: block_size 기본값 36→72봉
  - 36봉(1.5일) → 72봉(3일): 추세 성분 보존 강화
  - PAPER_SIM_BLOCK_SIZE 환경변수로 오버라이드 가능

## SIM 결과 요약

### Paper (Walk-Forward 1h봉, block=72)
- BTC: **7/22 PASS** — price_action_momentum(Sh5.21), momentum_quality(Sh3.76), cmf, volume_breakout, order_flow_imbalance_v2, htf_ema, positional_scaling
- ETH: **11/22 PASS** — supertrend_multi(4/4, Sh5.54), cmf(Sh6.23), 외 9종
- SOL: **4/22 PASS** — cmf(Sh4.37), momentum_quality(Sh4.34), order_flow_imbalance_v2, volatility_cluster

### OOS Bundle (4h봉)
- **0/5 PASS** — 4h GBM 합성 IS Sharpe 전부 음수 유지
- OOS Sharpe std: 3.4~6.4 (불안정, 합성 데이터 한계)

## 테스트 현황
- **8,127 passed** (회귀 없음)

## 다음 사이클: 236 (236 mod 5 = 1 → B(리스크) + D(ML) + F)
- B: PASS 전략(cmf/momentum_quality/ofi_v2) Kelly fraction 최적화
- D: order_flow_imbalance_v2 피처 중요도 분석
- F: 크로스-심볼 일관성 원인 분석, run_bundle_oos block_size 확인
======================================================================
