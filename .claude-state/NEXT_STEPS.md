# Next Steps

_Last updated: 2026-05-20 (Cycle 183 C+B+F+SIM 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 183 완료
- 183 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** 패턴 ✅
- 다음 Cycle 184: **184 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (지속)

**Cycle 183 시뮬레이션 결과 (Synthetic data):**
- paper_simulation (1h, BTC, 8 windows): 0/22 PASS
- bundle_oos (4h, dry-run, 9 folds): 0/5 PASS
- ⚠️ Bybit API SSL 차단으로 합성 데이터만 사용. 실제 데이터 결과 아님.
- **데이터 기간 확대 완료**: 6개월→12개월, 윈도우 2→8개 (통계 검증력 개선)

**과적합 근본 원인 (F 리서치 결과):**
1. WalkForwardOptimizer factory 함수가 params를 전략에 전달하지 않음 → IS 최적화 무의미
2. 355개 전략 테스트 → Deflated Sharpe: IS Sharpe 기준 1.0→2.5 상향 필요
3. OOS Sharpe std > 3 (fold별 -11~+6) → 통계적 노이즈 수준
4. 2025-2026 ETF 효과: BTC 변동성 구조 변화로 기존 파라미터 무효화

### 🎯 Cycle 184 권장 작업 (184 mod 5 = 4 → D+E+F)

#### D(ML): WalkForwardOptimizer factory 함수 수정 (최우선)
- `src/backtest/walk_forward.py` 312~327행: `factory(params)` 호출 시 params를 실제로 전략 생성자에 주입
- 각 전략 `__init__`이 kwargs를 받도록 수정 (EmaCrossStrategy(fast=params['fast'], ...))
- IS 최적화가 실제로 작동하게 된 후 OOS 성과 재측정

#### D(ML): OOS Sharpe 표준편차 필터 추가
- `RollingOOSValidator`에 fold별 OOS Sharpe std 필터 추가
- `oos_sharpe_std > 1.5`이면 FAIL (현재 std > 3인 전략이 다수)

#### E(실행): 거래 0건 전략 3개 파라미터 완화
- volume_breakout: ATR 필터 범위 확대 (0.3~5.0 → 0.1~10.0)
- dema_cross: 거리 필터 완화 (1% → 0.5%)
- price_cluster: threshold 확대 (0.2% → 0.5%)
- 완화 후 OOS walk-forward 재검증 필수

#### F(리서치): IS Sharpe 임계값 재검토
- 현재 QUALITY_AUDIT.csv 기준 Sharpe >= 1.0, PF >= 1.5
- DSR 보정 후 권장 기준: IS Sharpe >= 2.5
- QUALITY_AUDIT.csv에서 IS Sharpe >= 2.5 전략만 필터링하여 subset 검증

### ✅ Cycle 183 완료 사항

#### C(데이터): 데이터 인프라 개선 ✅ COMPLETE
- paper_simulation.py: 6→12개월 (8640봉), MIN_WINDOWS 2→3
- enrich_indicators(): Supertrend 미리 계산 (3 configs)
- walk-forward 윈도우: 2→8개 (O(n²) bottleneck 해결)

#### B(리스크): 버그 수정 ✅ COMPLETE
- WalkForwardValidator.validate() IS/OOS 데이터 누수 버그 수정
- adjust_for_regime() 불필요한 clipping 제거
- check_parameter_ratio() 유틸 추가
- manager.py flash_crash 음수 전용으로 수정 (양수 급등은 트리거 안 함)

#### BUG FIX: 기존 실패 테스트 6종 수정 ✅
- features.py: 빈 DataFrame KeyError 방어 (build, build_features_only)
- test_features_drift_edge_cases.py: PageHinkleyDriftDetector (lambda_val→lambda_, alpha→delta), CUSUM (delta→k) 파라미터명
- test_kelly_sizer_regime_edge_cases.py: max_fraction 클리핑 파라미터 조정
- test_risk_manager_edge_cases.py: consecutive_losses 테스트 수정 (check→record_trade_result), large_positive_price_move flash_crash 버그 수정
- test_ml_pipeline_edge_cases.py: pytest.warns(None) deprecated 구문 제거

#### F(리서치): 과적합 해결 방안 ✅ COMPLETE
- DSR: IS Sharpe >= 2.5 기준 상향 권고
- OOS std 필터 필요성 확인
- factory 함수 버그가 핵심 원인으로 확인

---

### 📋 Paper Trading 자동화 판정 기준 (Cycle 179 F 리서치 결과)

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |

---

### 📊 Strategy Performance Reference (Real Data — ⚠️ IS only, OOS 미검증)

| Strategy | Sharpe | Win% | PF | Trades | MDD | Regime |
|----------|--------|------|-------|--------|-----|--------|
| cmf | 6.85 | 57% | 2.29 | 28 | 4.3% | TREND |
| wick_reversal | 6.51 | 54% | 2.03 | 35 | 3.5% | RANGE |
| volume_breakout | 5.91 | 60% | 2.66 | 15 | 2.2% | TREND |
| elder_impulse | 6.29 | 63% | 2.70 | 16 | 3.5% | TREND |
| value_area | 5.24 | 53% | 1.84 | 30 | 5.0% | RANGE |

**⚠️ 위 수치는 IS(In-Sample) 성과. OOS 검증 시 전략 전부 FAIL.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL
- 관리: https://claude.ai/code/routines/trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 183 완료 → Cycle 184 D(WalkForward factory 수정) + E(거래 0건 전략 완화) + F(DSR 기준 적용)
**최우선 과제**: factory(params) 버그 수정 → IS 최적화 실제 동작 → OOS 재측정
