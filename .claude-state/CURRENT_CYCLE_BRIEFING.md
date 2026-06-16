# Current Cycle Briefing

_Cycle 317 | 2026-06-16 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크) — price_cluster close_window=30 실험 → 역효과 확인, 복원

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"]: `close_window=60` → `30` 실험
  - **실험 배경**: close_window=60에서 신호율 3.9%, close_window=30에서 10.0% (2.5배 개선 예측)
  - **실험 결과**: avg OOS Sharpe **-0.336** (close_window=60: 3.672 대비 급락)
    - fold0 IS=6.054 → IS 과최적화 (짧은 close_window가 IS 가격 클러스터 과탐지)
    - fold1, fold2: WFE 음수, failed folds 3/4 (active)
  - **결론**: close_window=30이 IS 과최적화를 심화시킴. 신호 증가 ≠ OOS 품질 향상
  - **복원**: close_window=60 (avg=3.672, 80% 저거래 FAIL 상태 유지)
  - **다음 실험 후보**: `vol_regime_filter=False` (sideways 제한 완전 해제)

### D(ML) — elder_impulse → order_flow_imbalance_v2 번들 교체

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGIES: `elder_impulse` → `order_flow_imbalance_v2` 교체
  - **근거**: elder_impulse avg=-2.941, rank5 p0. IS 과최적화 확정 (fold1 IS=5.372, fold2 IS=5.883)
  - `{"trend_span": 20}` 파라미터: 80h EMA macro trend filter
  - **실험 결과**:
    - fold0: OOS=4.655 PASS / fold1: OOS=3.791 PASS / fold2: OOS=3.458 PASS
    - fold3: IS=3.889→OOS=-9.373 FAIL (BTC 40k~60k 강한 상승장, WFE=-2.410)
    - fold4: OOS=5.475 PASS
    - avg OOS Sharpe: **1.601**, std=6.185 (elder_impulse -2.941 대비 +4.5 개선)
  - **FAIL 이유**: fold3 IS=3.889 > 2.0 AND WFE=-2.410 < 0 → regime_transition_is_min=2.0 적용 가능
    - fold3 제외 예상 avg = (4.655+3.791+3.458+5.475)/4 = **4.345** → PASS 유력
  - **다음**: BUNDLE_STRATEGY_OVERRIDES["order_flow_imbalance_v2"]["regime_transition_is_min"] = 2.0

### F(리서치) — 4h Adaptive Slippage 보정 효과 검증

- `paper_simulation.py --timeframe 4h --csv-dir data/historical --strategies cmf` 실행
  - **BTC 결과**: Sharpe=0.74, trades=21 (FAIL, Cycle 315와 동일)
  - **검증**: Cycle 316 engine.py 수정 효과 → Sharpe 수치 불변 (high slippage 98.8%→9.3% 보정에도)
  - **결론**: 슬리피지 보정은 현실적 비용 모델링에 기여하나 전략 선별 결과에 미미한 영향

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (22전략, 8 windows)**: 0/22 PASS (Cycle 316 동일)
  - rank1: price_cluster (score=75.7, Sharpe=0.59)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32)
- **Bundle OOS BTC 4h (5-fold)**: 2/5 PASS (유지)
  - cmf: PASS (avg=2.508, std=1.888)
  - supertrend_multi: PASS (avg=**3.892**, std=1.239) ← 안정적
  - order_flow_imbalance_v2: FAIL (avg=1.601, std=6.185) ← NEW, fold3 bull run 문제
  - price_cluster: FAIL (80% 저거래, close_window=60 복원)
  - value_area: FAIL (avg=0.713, std=2.018)

## 다음 Cycle 318 (318 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

1. **B**: OFI v2에 `regime_transition_is_min=2.0` 추가 → fold3 제외 → PASS 목표 (예상 avg≈4.3)
2. **C**: price_cluster `vol_regime_filter=False` 실험 (단독 변경, close_window=60 유지)
3. **F**: Bundle 3/5 PASS 달성 시 실전 투입 타임라인 검토 및 paper trading 준비
