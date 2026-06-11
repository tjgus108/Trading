# Current Cycle Briefing

_Cycle 298 완료 — 2026-06-11_
_카테고리: C(데이터) + B(리스크) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **C(데이터)**: price_cluster bounce_pct 0.015→0.02
   - `paper_simulation.py`: price_cluster bounce_pct 0.015→0.02
   - 결과: avg_trades 11→12 (소폭 개선), Sharpe=3.72 유지 (bounce_pct 확대 부작용 없음)

2. **B(리스크)**: relative_volume rvol_buy_sell 1.2→1.1
   - `paper_simulation.py`: rvol_buy_sell 1.2→1.1
   - 결과: avg_trades 17→19 (개선!), PF=1.63 유지, consistency 1/8 유지

3. **F(리서치)**: order_flow_imbalance_v2 buy_thresh 파라미터화 + 0.22 시도
   - `src/strategy/order_flow_imbalance_v2.py`: buy_thresh, sell_thresh 생성자 파라미터 추가
   - buy_thresh=0.22 시도 → consistency 3/8→2/8 퇴보 → PAPER_SIM 오버라이드 제거

### 시뮬레이션 결과

- Paper Sim BTC 4h: 0/22 PASS
  - price_cluster score=74.9, Sharpe=3.72, trades=12 (bounce_pct=0.02)
  - relative_volume score=62.6, Sharpe=1.84, trades=19 (rvol=1.1)
  - momentum_quality score=64.5, Sharpe=1.82, trades=22
  - order_flow_imbalance_v2 consistency=2/8 ← buy_thresh=0.22 역효과 → 기본값 복원
- Bundle OOS BTC 4h: **2/5 PASS** (cmf, supertrend_multi) — Cycle 297과 동일
- 테스트: **8392 passed**

### 다음 사이클 (299) 방향

- 299 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)**
- D: price_cluster trades=12 한계 — 신호 발생 조건 완화 검토 (threshold 범위 확장)
- E: relative_volume 추가 필터 (EMA 또는 ATR 기반) → 4/8 PASS 목표
- F: order_flow_imbalance_v2 근본 분석 — 거래량 필터 강화 or 손절 조건 추가
