# Next Steps

_Last updated: 2026-05-28 (Cycle 224 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 224 완료
- 224 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** + SIM ✅
- 다음 Cycle 225: **225 mod 5 = 0 → A(품질) + B(리스크) + F(리서치)**

### 🔥 Cycle 224 SIM 주요 성과

#### Paper Simulation 결과 (합성 BlockBootstrap, 3심볼)
- **전체 0/22 PASS (3심볼 모두)** — 합성 데이터 + mc_p_value > 0.05 주요 원인
- **BTC/USDT Top 5 (Composite Score)**:
  1. `price_action_momentum` score=65.2 (Sharpe 5.64, trades 146)
  2. `momentum_quality` score=61.4 (Sharpe 4.67, trades 118)
  3. `lob_maker` score=60.2 (Sharpe 5.19, trades 125)
  4. `volume_breakout` score=57.2 (Sharpe 5.40, trades 94)
  5. `order_flow_imbalance_v2` score=55.3 (Sharpe 5.44, trades 90)
- **ETH/USDT Top 3**: momentum_quality(79.6), price_action_momentum(76.7), roc_ma_cross(73.9)
- **SOL/USDT Top 3**: supertrend_multi(86.3), momentum_quality(76.7), price_action_momentum(72.9)
- **크로스 심볼 공통 상위**: `momentum_quality`, `price_action_momentum`, `supertrend_multi` — 3심볼 모두 top 5

#### value_area `va_mult` 버그 수정
- **문제**: `_VA_MULT = 0.6`으로 상수 변경했지만 `__init__` default가 `va_mult=0.7`(하드코딩) → 실제 0.6 미적용
- **수정**: `__init__` default를 `_VA_MULT` 상수 참조로 변경 (모든 상수 동일하게 처리)
- **현재 결과**: value_area avg_trades=16 (0.7 기준) → 다음 실행 시 0.6 적용으로 trades 증가 예상
- 테스트 14개 전부 PASS

#### Bundle OOS 결과 (합성 GBM, BTC 4h)
- **0/5 PASS** (cmf, elder_impulse, wick_reversal, narrow_range, value_area 전부 FAIL)
- **Composite Rank**: value_area(76.3) > wick_reversal(58.7) > elder_impulse(52.0)
- **OOS Sharpe std 범위**: 3.4~6.4 → 매우 불안정 (합성 데이터 한계)
- **IS Sharpe 음수 진단**: cmf, wick_reversal IS 전부 음수 → GBM 구조적 부적합 재확인
- **run_bundle_oos.py ImportError 수정**: `except RuntimeError` → `except (RuntimeError, ImportError)` 추가

#### FAIL 원인 분석 (Paper Simulation)
- **1위**: `mc_p_value > 0.05` (우연 가능성) — 합성 데이터의 본질적 한계
- **2위**: `profit_factor < 1.5` — 슬리피지/수수료 후 PF 미달
- **3위**: `max_drawdown > 20%` — cmf 등 일부 전략 MDD 초과

### Cycle 224 D(ML) + E(실행) 성과
- **MLSignalGenerator에 RegimeAwareFeatureBuilder 연결** (`src/ml/model.py`)
- **feature_importance_report() 리포팅 메서드 추가** (`src/ml/model.py`)
- **RegimeGuardedStrategy 래퍼 구현** (`src/strategy/base.py`)
- **TWAP estimate_slippage 엣지 케이스 강화** (`src/exchange/twap.py`)

### 🎯 Cycle 225 권장 작업 (225 mod 5 = 0 → A(품질) + B(리스크) + F(리서치))

#### A(품질): 테스트 + 코드 품질
- `value_area` va_mult=0.6 적용 후 paper_simulation 재실행 → trades 변화 확인
- quality_audit 재실행하여 value_area PASS 여부 확인
- MLSignalGenerator regime_aware 추론 통합 테스트 추가

#### B(리스크): 리스크 관리 강화
- ✅ `FullCircuitBreakerAdapter` orchestrator 주입 완료 (Cycle 222b)
- `DrawdownMonitor` weekly/monthly 리셋 검증
- WFO plateau check 추가: 최적 파라미터 ±10% 범위 안정성 검증 (리서치 권장)

#### F(리서치): 실전 데이터 전략 방향성
- **크로스 심볼 공통 상위 3**: `momentum_quality`, `price_action_momentum`, `supertrend_multi`
  → 실거래소 데이터 검증 최우선 후보
- `elder_impulse`: fold 1 OOS Sharpe 3.794 (SOL에서도 top 5) → 특정 레짐 강점 가능성

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 — "실전 PASS"라 단정 금지

**상태**: Cycle 224 완료 → Cycle 225 A(품질) + B(리스크) + F(리서치)
**최우선 과제**: value_area va_mult 수정 효과 검증 + FullCircuitBreakerAdapter 주입
