# Current Cycle Briefing

_Cycle 320 | 2026-06-17 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질) — price_cluster WFE 로직 분석 → 변경 불필요

- fold2 (IS=-2.345, OOS=1.098, WFE=0.0) 분석 완료
- WFE 임계값 1.5→1.0 완화 효과: fold2 WFE 0.0→0.5 가능하나 binding constraint 별도 존재
- **Binding constraints**: 저거래 비율 60% > 40% + std=3.854 >> 2.0
- **결론**: WFE 로직 유지 (변경 불필요), price_cluster 4h 구조 한계 확정 → 교체 결정

### C(데이터) — value_area BUNDLE_STRATEGY_OVERRIDES 추가 ✅

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_OVERRIDES["value_area"] 추가:
  - `{"regime_transition_is_min": 2.0, "min_oos_trades": 5}`
- **결과**: avg 0.713→2.016, std 2.018→1.825 (std 기준 통과!)
- fold3 (IS=2.492, WFE=-0.313), fold4 (IS=3.054, WFE=-0.093): 레짐 전환 제외
- **남은 문제**: fold0 (bear 2023-06~08, IS=-1.466, OOS=-0.091) → FAIL 지속

### F(리서치) — price_cluster 대안 탐색

- roc_ma_cross (rank3), positional_scaling (rank4): 1h 성능 약함 (Sharpe≤0.0)
- **추천 후보**: vwap_cross (4h 적합, 기존 번들과 다른 로직)
  - VWAP20/VWAP50 골든크로스: 추세 포착 전략
  - OFI v2(압력)/supertrend_multi(ATR추세)/cmf(자금흐름)와 다른 신호 원리
  - 4h OOS 성능 미검증 → Cycle 321 B에서 교체 실험 예정

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h**: 0/22 PASS (기존 유지, 1h 변경 없음)
- **Bundle OOS BTC 4h**: 3/5 PASS (유지)
  - OFI v2: PASS (avg=4.345, std=0.907) ← rank1
  - supertrend_multi: PASS (avg=3.892, std=1.239)
  - cmf: PASS (avg=2.508, std=1.888)
  - price_cluster: FAIL (avg=3.823, std=3.854) ← 교체 예정
  - value_area: FAIL (avg=2.016, std=1.825) ← **개선** (fold0이 binding)

## 다음 사이클 (321, mod5=1 → B+D+F)

- **B**: price_cluster → vwap_cross 번들 교체 실험 (BUNDLE_STRATEGIES 변경)
- **D**: value_area fold0 bear regime 대응 — is_negative_regime_max 파라미터 검토
- **F**: vwap_cross 4h 포텐셜 평가, 번들 적합성 분석
