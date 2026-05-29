# Next Steps

_Last updated: 2026-05-29 (Cycle 243 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 239, 240, 241, 242, 243

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 239 | C+B+SIM+F | reconnect_gaps, cache_stats, MDD kill switch, vol_scaling |
| 240 | D+E+SIM+F | regime별 importance, feature drift, check_strategy_health |
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |

### 🎯 Cycle 244 작업 방향 (244 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): elder_impulse fold1 분석 → 앙상블 개선
- Bundle OOS에서 elder_impulse fold1이 유일 PASS fold (OOS Sharpe=3.794, PF=1.90)
- IS Sharpe=-2.859인데 OOS=+3.794 → 역방향(IS 나쁜데 OOS 좋음) 케이스 분석
- IS-OOS 방향이 역전되는 fold에 대한 weight 조정 고려
- `compute_ensemble_weight_recency()`에 fold_direction 인자 추가 검토

#### E(실행): min_oos_trades 강화 효과 검증
- value_area가 완전 제외된 것이 올바른 판단인지 검증
  - 시간프레임 변경(4h → 1h)으로 trades ≥ 10 달성 가능한지 확인
  - `BUNDLE_STRATEGIES`에서 value_area 타임프레임 조건 추가 또는 다른 검증 기준 적용
- 실행 모듈의 슬리피지 로깅 강화

#### F(리서치): IS 음수 → OOS 양수 역전 케이스 분석
- elder_impulse fold1: IS=-2.859, OOS=+3.794 — 왜 IS가 나쁜데 OOS가 좋은가?
- 원인 가설:
  1. GBM 합성 데이터에서 IS 구간이 특별히 불리한 시장 패턴
  2. elder_impulse 신호가 mean-reverting 성질
  3. IS 구간의 파라미터가 OOS에 과적합이 아닌 저적합(underfitting)
- 실거래소 데이터 검증 필요

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: supertrend_multi(Sharpe 6.06), momentum_quality(Sharpe 4.49), price_action_momentum(Sharpe 3.37)
- 테스트: 171 passed (Cycle 243 +2개 추가)
- min_oos_trades: 10 (이전 3에서 강화)
- PerformanceMonitor: DrawdownMonitor 레짐 연동, mdd_halt_pct 자동 조정(bull 25%, bear 15%)
