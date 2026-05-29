# Next Steps

_Last updated: 2026-05-29 (Cycle 241 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 238, 239, 240, 241

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 238 | E+A+SIM+F | rolling Sharpe 모니터, perturbation_check, block_size 24, regime death 리서치 |
| 239 | C+B+SIM+F | reconnect_gaps, cache_stats, MDD kill switch, vol_scaling, --perturbation-check CLI |
| 240 | D+E+SIM+F | regime별 importance, feature drift, check_strategy_health, max_position_by_orderbook |
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI extreme edge cases, 15개 신규 테스트 |

### 🎯 Cycle 242 작업 방향 (242 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): distribution_drift를 PerformanceMonitor에 통합
- PerformanceMonitor.check_all()에서 check_distribution_drift 호출 추가
- 전략별 baseline_returns 저장 메커니즘 (초기 N 거래 기록)
- warn 발생 시 on_alert 콜백 연동

#### D(ML): 앙상블 모델 Sharpe 안정성 개선
- OOS Sharpe std > 1.5 문제 해결: 앙상블 가중치에 안정성 패널티 추가
- WFE < 0 fold 원인 분석: IS Sharpe 음수인 경우 OOS Sharpe 기대값 진단
- narrow_range 전략: OOS Sharpe std 6.35 → 파라미터 범위 축소 방향

#### SIM: --perturbation-check 단독 실행
- supertrend_multi, price_action_momentum 대상 ROBUST/FRAGILE 판정
- top 전략의 parameter sensitivity 확인

#### F(리서치): Walk-Forward Efficiency (WFE) 개선 사례
- WFE 음수 비율 높은 경우의 해결 방법
- 적응형 파라미터 vs. 고정 파라미터 trade-off

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- 상위 3: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- 테스트: 8,280+ passed (Cycle 240 +31개)
- 신규: regime별 importance, feature drift, check_strategy_health, max_position_by_orderbook
