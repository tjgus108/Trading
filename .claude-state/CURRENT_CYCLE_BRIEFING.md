# Current Cycle Briefing

_Cycle 298 완료 — 2026-06-11_
_카테고리: C(데이터) + B(리스크) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **C(데이터)**: price_cluster bounce_pct 0.015→0.02
   - avg_trades 11→12 (marginal), Sharpe 3.63→3.72 유지, PF 2.21→2.17
   - 여전히 trades < 15이므로 추가 조정 필요

2. **B(리스크)**: relative_volume rvol_buy_sell 1.2→1.1
   - avg_trades 17→19 (개선), PF 1.57→1.63 (개선)
   - mc_p_value 0.256→0.155 (개선), 1/8 PASS 유지

3. **B(리스크) 실험**: volatility_cluster vol_thresh=0.7 시도 → 역효과
   - trades 14→21 but PF 1.14→0.88 역효과 → PAPER_SIM에서 제거 (기본값 0.6 복원)
   - 파라미터화 코드는 유지

4. **코드 개선**: walk_forward.py OOS Sharpe 윈소라이제이션
   - `_SHARPE_FOLD_CAP = 10.0` 추가, WFE 윈소라이즈와 동일 원칙
   - 극단 fold(e.g. -12.3)가 avg_sharpe/oos_std 왜곡하는 것 방지

### 시뮬레이션 결과

- Paper Sim BTC 4h: 0/22 PASS
  - price_cluster: score=71.5, Sharpe=3.72 (bounce_pct=0.02 효과 확인)
  - relative_volume: score=61.0, trades=19, PF=1.63, 1/8 PASS (rvol=1.1 효과)
  - order_flow_imbalance_v2: 3/8 PASS (변화 없음)
- Bundle OOS BTC 4h: **2/5 PASS** (cmf, supertrend_multi) ← 유지
- 테스트: **8392 passed**

### 다음 사이클 (299) 방향

- 299 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)**
- D: price_cluster bounce_pct=0.025 또는 0.03 시도
- E: relative_volume rvol=1.0 또는 mc_block_size=3 시도
- F: order_flow_imbalance_v2 극단 손실 윈도우 대처 (imbalance_ma 필터 강화)
