# Current Cycle Briefing

_Cycle 298 완료 — 2026-06-11_
_카테고리: C(데이터) + B(리스크) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **C(데이터)**: price_cluster bounce_pct 0.015→0.02
   - W5/W6 sideways에서 2/8 consistency 달성 (trades=17, 15)
   - score 70.8→74.6 (최고치)

2. **B(리스크)**: relative_volume rvol=1.1 실험 → 역효과 확인 → 1.2 복원
   - rvol=1.1: trades 개선 but PF 1.40/1.36으로 하락
   - `engine.py` consec_loss_scale_threshold=5 추가 (연속 손실 포지션 축소)

3. **F(리서치)**: order_flow_imbalance_v2 trend_span 파라미터 추가
   - trend_span=20: 3/8 PASS 유지 (극단 손실 완화 효과 미미)
   - trend_span=50 시도: 1/8로 감소 (EMA50 과도한 필터링) → 20 유지

### 시뮬레이션 결과

- Paper Sim BTC 4h: **0/22 PASS** (price_cluster 2/8 consistency 최초 달성)
- Bundle OOS: **2/5 PASS** (cmf, supertrend_multi - Cycle 297과 동일)
- 테스트: **8392 passed**

### 다음 사이클 (299)

- **D(ML) + E(실행) + F(리서치)**
- price_cluster 2/8 기반으로 regime-aware 전략 스위칭 검토
- cmf/supertrend_multi Bundle OOS PASS → Paper Trading 실전 검토
- order_flow_imbalance_v2 cumulative delta window 단축 실험
