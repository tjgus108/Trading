# Next Steps

_Last updated: 2026-05-29 (Cycle 242 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 238, 239, 240, 241, 242

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 238 | E+A+SIM+F | rolling Sharpe 모니터, perturbation_check, block_size 24, regime death 리서치 |
| 239 | C+B+SIM+F | reconnect_gaps, cache_stats, MDD kill switch, vol_scaling, --perturbation-check CLI |
| 240 | D+E+SIM+F | regime별 importance, feature drift, check_strategy_health, max_position_by_orderbook |
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI extreme edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |

### 🎯 Cycle 243 작업 방향 (243 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): run_bundle_oos 저거래 필터 개선
- value_area처럼 fold당 trades < 10인 경우 → Sharpe 신뢰구간 너무 넓음
- `run_bundle_oos.py`: MIN_OOS_TRADES=3 → 10으로 강화 (현재 3)
- 또는: trades < 10 fold는 결과에서 제외하고 remaining fold로 pass/fail 판정

#### B(리스크): DrawdownMonitor + 레짐 전환 연동 강화
- regime_change_alert 호출 시 DrawdownMonitor threshold 자동 조정
- bull 레짐: mdd_threshold 20% → 25% 완화
- bear 레짐: mdd_threshold 20% → 15% 강화
- PerformanceMonitor.regime_change_alert() 확장

#### SIM: 시뮬레이션 환경 대응
- SSL 차단 환경 → 합성 데이터 결과만 사용
- perturbation_check 단독 실행: supertrend_multi, price_action_momentum ROBUST/FRAGILE 판정
- narrow_range 파라미터 범위 축소 효과 검증 (합성 데이터)

#### F(리서치): 앙상블 가중치 안정성 사례
- stability_penalty 효과 실증 사례 수집
- compute_ensemble_weight vs compute_ensemble_weight_recency 비교
- Sharpe std < 1.5 달성 사례 분석

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8318+ passed (Cycle 242 +11개 추가)
- 신규: PerformanceMonitor drift 통합, ensemble stability penalty, set_baseline 메서드
