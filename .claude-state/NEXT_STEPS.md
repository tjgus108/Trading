# Next Steps

_Last updated: 2026-05-27 (Cycle 224 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 224 완료
- 224 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** ✅
- 다음 Cycle 225: **225 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 224 주요 성과
- **MLSignalGenerator feature_names 버그 수정**: `load()` 시 `feature_names` + `trained_regime` 저장 → `predict()` 에서 reindex 필터링
  - Regime-aware 모델 학습 후 inference 시 피처 dim 불일치 방지
- **TWAP price_limit 버그 수정**: `runner.py`에서 `signal.entry_price`를 TWAP limit으로 전달
  - 기존: price_limit=None → live mode filled_price fallback 0.0 → impl_shortfall_bps 오계산
  - 수정: signal.entry_price를 price_limit으로 전달 → 정확한 슬리피지 추정

### 🎯 Cycle 225 권장 작업 (225 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 백테스트 품질 재검증
- 테스트 커버리지 확인: `python3 -m pytest tests/ --co -q | wc -l` → 7991개 테스트
- `MLSignalGenerator` 테스트 추가: feature_names 필터링 검증 (새 유닛 테스트)
  - 파일: `tests/test_ml_signal_generator.py` (있으면 수정, 없으면 신규)
  - 케이스: regime-aware 모델 로드 후 predict → 피처 필터링 동작 확인
- `scripts/quality_audit.py` 상태 확인 — QUALITY_AUDIT.csv 최신 여부 점검

#### C(데이터): 데이터 인프라
- `src/data/feed.py` WebSocket 안정성 확인: reconnect 로직 검증
- `RegimeAwareFeatureBuilder` predict 경로: `build_features_regime()` 활용 여부 확인
  - `MLSignalGenerator.predict()` 에서 regime 인식 추론 지원 검토
  - 현재는 FeatureBuilder (all features) → 미래에 RegimeAwareFeatureBuilder 통합 옵션
- DataFeed 캐시 전략: `fetch()` 중복 호출 방지 확인

#### F(리서치): 실전 데이터 전략 방향성
- **최우선 실거래소 검증 후보** (Paper Sim + Bundle OOS 기반):
  1. `momentum_quality`: Sharpe 6.63, PF 1.97, Trades 123 (합성 데이터 최고 Sharpe)
  2. `price_action_momentum`: Sharpe 6.59, PF 1.81, Trades 163 (높은 거래 수)
  3. `supertrend_multi`: Sharpe 3.97, PF 1.52 (안정적 중위)
- `value_area` 4h: avg trades 3.9 (여전히 저거래) → NEXT 기회에 신호 완화
- OOS Sharpe std > 4.0 전략 (cmf, wick_reversal): GBM 합성 구조적 부적합 → 실거래 필수

### ⚠️ 핵심 인사이트 (Cycle 224)

#### 시뮬레이션 분석
- **Paper Sim 새 TOP**: `price_action_momentum` (Sharpe 6.59) — 이전 Cycle에서 3위, 이번 1위
- **공통 상위 전략**: `momentum_quality` (Sharpe 6.63, PF 1.97) — 두 시뮬 모두 상위 3위 이내
- **합성 데이터 한계 재확인**: 0/4 consistency → 합성 GBM에서 window별 변동이 너무 큼
- **cmf 역설**: Bundle OOS IS Sharpe 전부 음수지만 Paper Sim return +93.5% → 데이터 시드 의존성

#### 코드 개선 연속성
- `MLSignalGenerator.predict()` feature filtering 완료 (Cycle 224)
- TWAP price_limit 연결 완료 (Cycle 224)
- FullCircuitBreakerAdapter orchestrator 주입 완료 (Cycle 221, 확인 Cycle 224)
- `adaptive_stop_multiplier` regime 연결 완료 (Cycle 222 → 223 파이프라인 연결)

#### B(리스크): Risk Management 검증 ✅ COMPLETE
- CircuitBreaker 플래시크래시 리셋 버그 수정
- KellySizer, DrawdownMonitor, PerformanceMonitor 검증 완료
- PortfolioOptimizer VaR/CVaR 정상

**상태**: Cycle 224 완료 → Cycle 225 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: MLSignalGenerator feature_names 유닛 테스트 추가 + momentum_quality 실거래소 검증 준비
