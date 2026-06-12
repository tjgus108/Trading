# Current Cycle Briefing

_Cycle 300 완료 — 2026-06-12_

## 완료된 작업

### A+F: price_cluster 상대적 ATR vol_regime_filter 구현
- `src/strategy/price_cluster.py`: `_atr_ratio_relative()` 메서드 추가
  - ATR(14)/ATR_MA(20) 비율로 시장 레짐 판별
  - 비율 > 1.5 → 추세/변동성 장 → 신호 억제
  - 비율 ≤ 1.5 → sideways 또는 모호 → 신호 허용
  - 데이터 부족 시 중립값(1.0) 반환 → 과도한 억제 방지
- 결과: score 71.5→**74.8** (+3.3), trades=12 유지, 2/8 PASS 유지
- 이전 절대값(thresh=0.025): trades 12→5, 0/8 PASS (역효과)
- 상대값(thresh=1.5): trades 12 유지, 2/8 PASS 유지 ✅

### C: order_flow_imbalance_v2 파라미터화 + 실험
- `src/strategy/order_flow_imbalance_v2.py`: buy_thresh/sell_thresh 파라미터 추가
- buy_thresh=0.30 실험: 3/8→1/8 PASS 역효과 → **기본값(0.25) 복원**
- 코드 기능 유지 (향후 실험 용이)

## 시뮬레이션 요약

| 구분 | 결과 |
|------|------|
| Paper Sim PASS | 0/22 (price_cluster 2/8 일관성) |
| Bundle OOS PASS | 2/5 (cmf, supertrend_multi) |
| 테스트 스위트 | 8392 passed, 23 skipped |

## 다음 사이클 (301): B(리스크) + D(ML) + F(리서치)
- price_cluster trades 증가 검토 (bounce_pct 0.02→0.025)
- order_flow_imbalance_v2 3/8 PASS 복원 확인
- momentum_quality PF < 1.5 필터링 강화 검토
