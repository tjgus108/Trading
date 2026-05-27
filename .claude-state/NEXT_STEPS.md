# Next Steps

_Last updated: 2026-05-28 (Cycle 222 B+D+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 222 완료
- 222 mod 5 = 2 → B(Risk) + D(ML) + SIM + F(리서치) 완료
- 다음 Cycle 223: **223 mod 5 = 3 → E(실행) + A(품질) + F(리서치)**

### 🔥 Cycle 222 주요 성과
- **orchestrator FullCircuitBreakerAdapter 주입**: 풀버전 CB(rapid_decline, ATR surge, correlation throttle) → 레거시 fallback 포함
- **paper_simulation fail_reasons 리포트**: 윈도우별 실패 원인 Counter 집계 + 전체 빈도 상위 10
- **ADWIN 모델 헬스 섹션**: DualGateADWINMonitor 기반 드리프트/Retrain 권고 리포트
- **value_area 파라미터 조정**: va_mult 0.7→0.6, vol_filter_mult 0.8→0.7 (trades 부족 해결)
- **리서치**: 73% 봇 6개월 실패, WFO 메타-과적합, RegimeGuardedStrategy 필수

### Cycle 222 상위 전략 (BTC, 합성 데이터 — 방향성 참고만)
| Rank | Name | AvgReturn | AvgSharpe | AvgPF | AvgTrades |
|------|------|-----------|-----------|-------|-----------|
| 1 | price_action_momentum | +97.73% | 6.03 | 1.75 | 154 |
| 2 | momentum_quality | +61.26% | 5.28 | 1.74 | 123 |
| 3 | lob_maker | +52.99% | 3.62 | 1.45 | 120 |
| 4 | volume_breakout | +40.74% | 3.82 | 1.62 | 85 |
| 5 | volatility_cluster | +33.89% | 4.22 | 1.74 | 79 |

### 🎯 Cycle 223 권장 작업 (223 mod 5 = 3 → E(실행) + A(품질) + F(리서치))

#### E(실행): RegimeGuardedStrategy + Paper Trading 검증
- RegimeGuardedStrategy 래퍼 구현 (전략 코드 무수정으로 레짐 필터 적용)
  - BaseStrategy 래퍼: `__init__(inner_strategy, regime_detector)`
  - `generate_signal()` 오버라이드: 레짐 체크 후 inner 신호 통과/차단
- Paper Trading dry_run 전체 파이프라인 실행 검증
- value_area 조정된 파라미터로 재시뮬레이션 확인

#### A(품질): 테스트 커버리지 + fail_reasons 활용
- orchestrator FullCircuitBreakerAdapter 통합 테스트 강화
- paper_simulation fail_reasons/model_health 리포트 정합성 테스트
- MC permutation test가 합성 데이터에서 과도하게 작동하는지 조사

#### F(리서치): 실거래소 데이터 검증 + 레짐 전략
- 실거래소 데이터 확보 시 최우선 검증: price_action_momentum, momentum_quality, value_area
- RegimeGuardedStrategy 적용 시 기대 성과 변화 리서치
- 소규모 봇의 중빈도 전략 수익성 사례 추가 조사

### ⚠️ 핵심 인사이트 (Cycle 222)
- **0/22 PASS 상태 지속**: MC permutation test가 합성 데이터에서 과도하게 작동하는 의심
- **FullCircuitBreakerAdapter 완전 통합**: orchestrator → 풀버전 CB, fallback 안전장치 포함
- **리서치 핵심**: 73% 봇 6개월 실패(과최적화), WFO도 메타-과적합 가능, 합성 OOS Sharpe std ~4.5는 합성노이즈 반응 신호
- **RegimeGuardedStrategy는 필수**: 레짐 감지 없는 봇은 플래시크래시에 취약 (2025년 5월 사례)
- **CB 실전 표준**: 일 손실 -3~5%, peak -20% 도달 시 즉시 정지

### 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 222 B+D+SIM+F 완료 → Cycle 223 E(실행) + A(품질) + F(리서치)
**최우선 과제**: RegimeGuardedStrategy 구현 + MC test 합성데이터 편향 조사 + orchestrator FullCB 통합 테스트
