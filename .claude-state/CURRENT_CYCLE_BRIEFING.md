# Current Cycle Briefing

_Cycle 339 | 2026-06-20 | D(ML) + F(리서치)_

## 완료된 작업

### F(리서치): atr_multiplier_tp=3.5→4.0 실험 → FAIL → 즉시 revert

- **실험**: `engine.py` `atr_multiplier_tp=3.5→4.0` (R:R=2.67, 이론 PF=1.63)
- **Bundle OOS 결과**: **1/5 PASS** (catastrophic regression)
  - cmf: FAIL (std=2.858, fold2 Sharpe=-2.443)
  - order_flow_imbalance_v2: FAIL (fold3 OOS=-9.373, std=2.680)
  - vwap_cross: FAIL (fold1 Sharpe=-2.270, std=2.929)
  - value_area: FAIL (fold3,4 negative OOS Sharpe)
  - supertrend_multi: PASS (레짐전환 fold4 제외)
- **즉시 revert**: tp=3.5 복원 → Bundle OOS **5/5 PASS 복원 확인** ✅
- **결론**: atr_multiplier_tp=4.0 사용 불가. 번들 전략들의 청산 구조와 충돌.
  - TP 원거리화 → 손실 노출 기간 증가 → 전략별 risk 구조 붕괴
  - **주의 사항 추가**: atr_multiplier_tp 상향 실험 금지 (영구)

### D(ML): ML 모델 재훈련 시도 + ADWIN drift 분석

- ADWIN drift (Cycle 338 paper sim): 3개 심볼 모두 "drift YES, retrain count=3"
  - Feature drift 0/3이지만 ADWIN 윈도우 수축 3회 (레짐 변화 패턴)
- **재훈련 결과**: 모두 FAIL
  - BTC: train=0.755, val=0.500, test=0.512 → FAIL (< 0.55)
  - ETH: train=0.778, val=0.413, test=0.447 → FAIL
  - SOL: train=0.756, val=0.448, test=0.461 → FAIL
  - 심각한 과적합: train 0.75-0.78 vs test 0.45-0.51
  - 기존 모델 유지 (새 모델 저장 없음)
- **결론**: 현재 피처 셋으로는 55% 정확도 달성 불가
  - 향후 방향: 피처 수 감소 + GradientBoosting 앙상블

## 시뮬레이션 결과 (Cycle 339)

- **테스트**: 56 engine tests PASS ✅

- **Bundle OOS BTC 4h (atr_tp=4.0)**: **1/5 PASS** → 즉시 revert
- **Bundle OOS BTC 4h (atr_tp=3.5 복원)**: **5/5 PASS** ✅
  - rank1: order_flow_imbalance_v2 (avg=4.345)
  - rank2: supertrend_multi (avg=3.892)
  - rank3: value_area (avg=3.069)
  - rank4: vwap_cross (avg=3.047)
  - rank5: cmf (avg=2.508)

- **Paper Sim BTC 1h (atr_tp=4.0 실험 중 실행)**: 아래 참조 (실험 데이터)

## 다음 사이클 (340 mod 5 = 0): D(ML) + E(실행) + F(리서치)

- **F(리서치)**: R:R 개선 대안 탐색
  - atr_multiplier_sl=1.5→1.2 실험 (SL 좁히기, R:R=2.92) - 단, WR 하락 가능
  - OR min_hold_bars=4 효과 분석 (1h 재진입 쿨다운)
  - OR price_cluster 트렌드 필터 (ATR slope 기반)
- **D(ML)**: 피처 엔지니어링 개선 (과적합 해소)
- **E(실행)**: live_paper_trader.py 상태 점검
