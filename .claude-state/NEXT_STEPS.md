# Next Steps

_Last updated: 2026-05-27 (Cycle 223 C+B+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 223 완료
- 223 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** ✅
- 다음 Cycle 224: **224 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 223 주요 성과
- **regime → pipeline 연결**: `TradingPipeline.current_regime` 속성 추가
  - `orchestrator.run_once()` → `self._pipeline.current_regime = regime`
  - `_run_inner()` → `evaluate(..., regime=self.current_regime)` 전달
  - Cycle 222에 추가한 `adaptive_stop_multiplier(regime=...)` 이 실제로 작동
- **SSL transient 분류**: `_is_transient_error()` SSL/cert string 감지 추가
  - `ccxt.NetworkError` 미래핑 SSL 에러도 exchange fallback 트리거

### 🎯 Cycle 224 권장 작업 (224 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 모델 + Walk-Forward 파이프라인
- `src/ml/` RF 모델 피처 중요도 분석: 어떤 피처가 synthetic/real 데이터에서 살아남는지
- Walk-Forward 파이프라인에서 regime 기반 피처 선택 적용 검토
  - `RegimeAwareFeatureBuilder` 연결 상태 확인
- MonteCarlo seed 다양성: `scripts/paper_simulation.py`에서 MonteCarlo seed 랜덤풀 사용 검토
  - 현재 `seed=None` → OK (이미 random). 실제 코드 확인 완료.

#### E(실행): TWAP + 슬리피지 모델
- `src/exchange/twap.py`: TWAP 실행기 검증 — 슬리피지 모델 vs 실제 체결 비교
- `scripts/live_paper_trader.py` 실행 점검 (로컬 paper trading 시뮬)
- `FullCircuitBreakerAdapter` orchestrator 주입 검토
  - Cycle 221에 어댑터 추가, Cycle 223에도 미주입 → 다음 사이클 E 작업 시 고려

#### F(리서치): 실전 데이터 전략 방향성
- `momentum_quality` / `supertrend_multi`: BTC 1~2위 (PF 1.5+) → 실거래소 검증 최우선
- `value_area` 4h: avg trades 3.6 (너무 희소) → `min_volume_pct` 완화 또는 `atr_threshold` 축소 검토
  - value_area 관련 테스트 확인 후 파라미터 조정 (strategy 파일 직접 수정은 금지)
- `elder_impulse`: fold 1 OOS Sharpe 3.794 → 특정 구간 강점, 실거래소 구간 분석 필요

### ⚠️ 핵심 인사이트 (Cycle 223)

#### 시뮬레이션 분석
- **합성 데이터 한계 재확인**: 전부 0/N consistency
  - `low_pf` + `low_consistency` 여전히 주요 FAIL 원인
  - IS Sharpe 전부 음수인 전략 (cmf, wick_reversal) → GBM 합성 구조적 부적합
- **BTC 공통 1~2위**: `momentum_quality` (Sharpe 3.96, PF 1.56), `supertrend_multi` (Sharpe 3.58, PF 1.60)
  - 이 전략들은 실거래소 데이터 검증 시 최우선 후보
- **Bundle OOS**: OOS Sharpe std 3.4~6.4 → 매우 불안정 (실거래소 필요)

#### 코드 개선 연속성
- `adaptive_stop_multiplier` regime 연결 완료 (Cycle 222 → Cycle 223 파이프라인 연결)
- `DrawdownMonitor` weekly/monthly 리셋 완료 (Cycle 222)
- `FullCircuitBreakerAdapter` 생성 완료 (Cycle 221) → orchestrator 주입은 Cycle 224 E 작업에서

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 가능

**상태**: Cycle 223 완료 → Cycle 224 D(ML) + E(실행) + F(리서치)
**최우선 과제**: FullCircuitBreakerAdapter orchestrator 주입 + TWAP 검증
