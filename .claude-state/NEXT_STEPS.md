# Next Steps

_Last updated: 2026-05-27 (Cycle 220 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 220 완료
- 220 mod 5 = 0 → **D(ML) + E(실행) + F(리서치)** ✅
- 다음 Cycle 221: **221 mod 5 = 1 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 220 주요 성과
- **should_retrain_by_ewma()**: EWMA 경고 연속 5회 시 재학습 권고
- **get_model_health()**: accuracy/trend/drift 요약 dict
- **orchestrator CF-VaR 주입**: KellySizer(0.25) + DrawdownMonitor(8%) + PortfolioOptimizer(5%) → RiskManager
- **15분 윈도우 Flash Crash Detection**: 단일캔들 -10% 또는 15분 내 -10% → 60캔들 cooldown
- **value_area 안정화**: std_floor_pct=0.005 + vol_filter_mult=0.8

### 🎯 Cycle 221 권장 작업 (221 mod 5 = 1 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 테스트 커버리지 + 기존 이슈 정리
- circuit_breaker.py 강화 버전 → RiskManager 통합 (현재 manager.py 내 간소화 버전과 분리됨)
- 기존 flaky 테스트 45건 중 해결 가능한 것 수정
- orchestrator 새 파라미터 주입 통합 테스트 추가

#### C(데이터): WebSocket 안정성 + 온체인 데이터
- WebSocket ConnectionHealthMonitor 개선
- 온체인 데이터 stub (VPIN/OrderFlow) 정확도 검증 후속
- DataFeed 레짐별 캐시 만료의 실전 효과 검증

#### F(리서치): RegimeGuardedStrategy + 실전 데이터 전략
- BaseStrategy에 _regime_check() 훅 설계 (3줄, 하위 호환) vs RegimeGuardedStrategy 래퍼 비교
- adaptive_stop_multiplier()에 regime 파라미터 추가 가능성
- 실데이터 PASS 전략 0개 → 어떤 전략이 실전에서 유망한지 방향성 리서치

### ⚠️ 핵심 인사이트 (Cycle 220)
- **circuit_breaker.py 미연결**: 강화 버전(flash_crash_pct, rapid_decline 등)이 manager.py 내 간소화 CB와 분리됨
- **레짐 필터 래퍼**: RegimeGuardedStrategy 패턴이 각 전략 무수정으로 레짐 필터 적용 가능
- **플래시 크래시**: 즉시 전량 청산 비권장, 50%→대기→나머지 단계적 축소가 실전 효과적
- **3Commas/Freqtrade 패턴**: bear 전환 시 DCA step 50% 축소, custom_stoploss()에서 레짐별 SL 동적 조정

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 220 완료 → Cycle 221 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: circuit_breaker.py 통합 + RegimeGuardedStrategy 설계 + 테스트 정리
