# Next Steps

_Last updated: 2026-05-27 (Cycle 222 B+D+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 222 완료
- 222 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** ✅
- 다음 Cycle 223: **223 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 222 주요 성과
- **DrawdownMonitor**: `reset_weekly()` / `reset_monthly()` 추가 (주간/월간 CB 해제)
- **adaptive_stop_multiplier**: `regime` 파라미터 + `_REGIME_STOP_BOUNDS` 테이블 추가
  - CRISIS/HIGH_VOL → 최소 2.5/2.0, TREND_UP/BULL → 최대 1.5
- **paper_simulation.py**: 윈도우별 `fail_reasons` 수집 + FAIL 진단 섹션 추가

### 🎯 Cycle 223 권장 작업 (223 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): DataFeed + 온체인 데이터
- `DataFeed.fetch()`: 캐시 전략 최적화 — 동일 심볼/timeframe 재요청 시 TTL 체크
- VPIN/OrderFlow 지표 정확도: `src/data/` 내 `order_flow.py` 검토
- BlockBootstrap 시드 다양성: 현재 seed 고정 → 랜덤 seed pool 사용 검토

#### B(리스크): RiskManager + 테스트 강화
- `evaluate()` regime 파라미터가 실제 orchestrator.py에서 사용되도록 연결
  - 현재는 `adaptive_stop_multiplier`에 연결했지만, orchestrator가 regime을 전달해야 함
- `FullCircuitBreakerAdapter` → orchestrator.py에 실제 주입 (현재 레거시 CB만 사용)
- VaR/CVaR 계산 정확도 검증: `estimate_var_cvar()` 합성 데이터 vs 실데이터 비교

#### F(리서치): 실전 데이터 전략 방향성
- `momentum_quality` / `price_action_momentum`: BTC/ETH 모두 상위권 → 실거래소 검증 1순위
- FAIL 진단 결과: `low_pf` 빈발 → PF 임계값(1.5) 완화 또는 전략 파라미터 grid 조정 검토
  - 현재 PF ≥ 1.5 기준이 합성 데이터에서 너무 엄격할 수 있음
- `dema_cross` SOL 1h: Sharpe 2.85, PF 2.68, 단 12 trades → trades 수 조건 완화 검토

### ⚠️ 핵심 인사이트 (Cycle 222)

#### 시뮬레이션 분석
- **합성 데이터 한계 재확인**: 모든 전략 0/4 consistency
  - `low_pf`가 가장 빈번한 FAIL 원인 → 합성 GBM 데이터에서 PF 1.5 달성이 어려움
  - 실거래소 데이터라면 다른 결과 예상
- **BTC/ETH 공통 1-2위**: `momentum_quality` (BTC), `price_action_momentum` (BTC/ETH)
  - 이 전략들은 실거래소 데이터 검증 시 최우선 후보
- **Bundle OOS**: value_area 4/9 fold PASS이나 avg trades 3.6 → 신호 희소
  - 다음 사이클에서 value_area의 min_volume_pct 파라미터 완화 검토

#### 코드 개선 연속성
- `DrawdownMonitor`: weekly/monthly 리셋 완료 → orchestrator에서 호출 시점 연결 필요
- `adaptive_stop_multiplier` regime 연결 완료 → orchestrator가 `RegimeDetector.detect()` 결과를 `evaluate()` regime 파라미터에 전달해야 효과 발휘
- `paper_simulation.py` fail_reasons 진단 → 다음 사이클에서 진단 결과 기반 파라미터 조정

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 222 완료 → Cycle 223 C(데이터) + B(리스크) + F(리서치)
**최우선 과제**: orchestrator.py에 regime 전달 연결 + FullCircuitBreakerAdapter 실제 주입
