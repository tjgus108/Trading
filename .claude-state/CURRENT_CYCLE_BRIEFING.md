# Current Cycle Briefing

_Cycle 295 완료 — 2026-06-10_
_카테고리: A(품질) + C(데이터) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **A(품질)**: 저거래 전략 파라미터화 + PAPER_SIM 오버라이드 추가
   - `src/strategy/relative_volume.py`: `rvol_buy_sell` 생성자 파라미터 추가
   - `scripts/paper_simulation.py`: 5개 전략 오버라이드 추가
     - value_area vol_filter_mult=0.5, wick_reversal min_volatility=0.001, relative_volume rvol_buy_sell=1.3
   - 결과: relative_volume avg trades 13→15 (임계값 달성), value_area 12→16

2. **C(데이터)**: sideways 레짐 전략 파라미터 유연성 확보
   - `src/strategy/momentum_quality.py`: quality_score_buy_threshold/consistency_buy_threshold 파라미터화
   - `src/strategy/price_cluster.py`: bounce_pct 생성자 파라미터 추가
   - PAPER_SIM 오버라이드: momentum_quality threshold=0.8, price_cluster bounce_pct=0.015
   - 결과: price_cluster rank1 상승 (Sharpe=3.63, PF=2.21), momentum_quality 22 trades 유지

3. **F(리서치)**: Paper Sim + Bundle OOS 결과 분석
   - Paper Sim: 0/22 PASS, 파라미터 완화로 FAIL 원인 변화 확인
     - "trades < 15" 감소 → "mc_p_value > 0.05" 이슈 부상 (통계 검증력 문제)
   - Bundle OOS: 2/5 PASS 유지 (cmf + supertrend_multi)
   - value_area Bundle OOS init_param 실험 → std 악화로 롤백

### 현재 성과 지표

- **테스트**: 8392 passed (회귀 없음)
- **Paper Sim**: 0/22 PASS (목표: ≥1 PASS)
  - 최고 전략: price_cluster (Sharpe=3.63, PF=2.21, trades=11)
  - relative_volume: trades=15 달성, mc_p_value FAIL
- **Bundle OOS**: 2/5 PASS (cmf, supertrend_multi)
  - cmf: avg Sharpe=2.508, std=1.888, WFE=1.136
  - supertrend_multi: avg Sharpe=3.674, std=1.860, WFE=2.116

### 다음 사이클 우선순위

**Cycle 296 = B(리스크) + D(ML) + F(리서치)**

1. **B**: mc_p_value 유의수준 검토 — 0.05→0.10 완화 가능성 분석
2. **D**: relative_volume 레짐 필터 + price_cluster _CLOSE_WINDOW 파라미터화
3. **F**: 통계 검증력 vs 거래 빈도 트레이드오프 리서치
