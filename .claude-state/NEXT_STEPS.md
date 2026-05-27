# Next Steps

_Last updated: 2026-05-27 (Cycle 221 A+C+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 221 완료
- 221 mod 5 = 1 → **A(품질) + C(데이터) + F(리서치)** ✅
- 다음 Cycle 222: **222 mod 5 = 2 → E(실행) + A(품질) + F(리서치)**

### 🔥 Cycle 221 주요 성과
- **quality_audit.py 로깅 사이드 이펙트 수정**: flaky 테스트 2건 해소
- **FullCircuitBreakerAdapter**: circuit_breaker.py 풀버전 → RiskManager 레거시 인터페이스 어댑터
- **ConnectionHealthMonitor 개선**: `reconnection_rate()`, `is_flapping()` 추가
- **WalkForwardValidator**: window result에 `fail_reasons` 추가 (진단 용이)

### 🎯 Cycle 222 권장 작업 (222 mod 5 = 2 → E(실행) + A(품질) + F(리서치))

#### E(실행): Paper Trading 검증 + TWAP 슬리피지
- Paper Trading dry_run 모드 전체 파이프라인 실행 검증
- TWAP 슬리피지 모델 정확도: dry_run vs 실제 비교 (합성 데이터 기반)
- orchestrator.py에 `FullCircuitBreakerAdapter` 실제 주입 (현재 레거시 CB만 사용)

#### A(품질): 테스트 커버리지 + RegimeGuardedStrategy
- `RegimeGuardedStrategy` 래퍼 구현 (전략 코드 무수정으로 레짐 필터 적용)
  - BaseStrategy 래퍼: `__init__(inner_strategy, regime_detector)`
  - `generate_signal()` 오버라이드: 레짐 체크 후 inner 신호 통과/차단
- orchestrator.py에서 FullCircuitBreakerAdapter 사용 테스트

#### F(리서치): 실전 데이터 전략 방향성
- `price_action_momentum`과 `momentum_quality`: 합성 Sharpe 최고 → 실거래소 데이터 검증 시 우선 순위
- `value_area` 저거래 fold 원인: vol_filter 파라미터 확인
- adaptive_stop_multiplier()에 regime 파라미터 추가 가능성 조사

### ⚠️ 핵심 인사이트 (Cycle 221)

#### 시뮬레이션 분석
- **OOS Sharpe std >> 1.5**: 합성 데이터 특성상 높은 분산 → 실거래소 데이터에서만 정확한 판단 가능
- **value_area 4/9 PASS**: 가장 유망한 후보. `std_floor_pct=0.005` + `vol_filter_mult=0.8` 효과 있음
- **price_action_momentum**: Paper Sim 1위 (Sharpe 6.68, PF 1.78, 167 trades) — 충분한 거래 신호
- **narrow_range**: fold 4,6,7 PASS (3/9) — 특정 레짐에서만 작동하는 전략으로 분류

#### 코드 개선 후속
- `WalkForwardValidator` window result에 `fail_reasons` 추가 완료
  - 이제 paper simulation이 window별 실패 이유를 보여줄 수 있음
  - scripts/paper_simulation.py에서 이 필드를 활용하도록 리포트 개선 가능 (다음 사이클)
- `FullCircuitBreakerAdapter` 완료 — orchestrator.py에서 실제 사용 가능

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 221 완료 → Cycle 222 E(실행) + A(품질) + F(리서치)
**최우선 과제**: RegimeGuardedStrategy 구현 + orchestrator FullCB 주입 + paper_sim 리포트 fail_reasons 활용
