# Next Steps

_Last updated: 2026-05-29 (Cycle 240 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 238, 239, 240

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 238 | E+A+SIM+F | rolling Sharpe 모니터, perturbation_check, block_size 24, regime death 리서치 |
| 239 | C+B+SIM+F | reconnect_gaps, cache_stats, MDD kill switch, vol_scaling, --perturbation-check CLI |
| 240 | D+E+SIM+F | regime별 importance, feature drift, check_strategy_health, max_position_by_orderbook |

### 🎯 Cycle 241 작업 방향 (241 mod 5 = 1 → A(품질) + C(데이터) + F(리서치))

#### A(품질): KS-test 기반 분포 drift 모니터 구현
- 리서치 결과 적용: ks_2samp으로 baseline vs recent 수익률 분포 비교
- PerformanceTracker 또는 별도 모듈에 `check_distribution_drift(baseline_returns, recent_returns)` 구현
- 2-signal 합의: KS p<0.05 + rolling Sharpe < 0.5 동시 충족 시 경고
- 파라미터 5개 이하 전략 필터링 유틸리티 검토

#### C(데이터): OFICalculator 극단값 로직 검증
- OFICalculator 극단 감지 로직 리뷰 및 엣지케이스 테스트 보강
- DataFeed 캐시 통계(get_cache_stats) 활용 패턴 검증

#### SIM: --perturbation-check 단독 실행
- CPU 경합 없이 단독으로 --perturbation-check 실행
- Top 전략 ROBUST/FRAGILE 판정 확인

#### F(리서치): 실전 봇 모니터링 대시보드 패턴
- 실전 트레이딩 봇의 모니터링 대시보드 best practice
- 어떤 메트릭을 실시간으로 추적하는지

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8,280+ passed (Cycle 240 +31개)
- 신규: regime별 importance, feature drift, check_strategy_health, max_position_by_orderbook
