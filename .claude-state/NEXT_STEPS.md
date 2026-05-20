# Next Steps

_Last updated: 2026-05-20 (Cycle 184 D+E+F+SIM 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 184 완료
- 184 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 185: **185 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (지속)

**Cycle 184 시뮬레이션 결과 (Synthetic data):**
- paper_simulation (1h, BTC, 22 strategies, 8 windows): 0/22 PASS
- bundle_oos (4h, dry-run, 5 strategies, 9 folds): 0/5 PASS
- ⚠️ Bybit API SSL 차단으로 합성 데이터만 사용. 실제 데이터 결과 아님.
- **OOS std 필터 추가**: 5/5 전략 std > 1.5 (3.16~6.15) → 불안정 추가 필터 동작 확인
- **factory 버그 수정**: IS 최적화 실제 작동 — 하지만 합성 데이터에서 효과 측정 어려움

### 🎯 Cycle 185 권장 작업 (185 mod 5 = 0 → A+C+F)

#### A(품질): IS Sharpe >= 2.5 subset 재검증
- QUALITY_AUDIT.csv에서 IS Sharpe >= 2.5 전략만 필터 (DSR 보정 기준)
- 현재 PASS 22개 중 몇 개가 >= 2.5인지 확인
- QUALITY_AUDIT.csv 기준 업데이트 고려 (Sharpe 1.0 → 2.5)

#### A(품질): 테스트 커버리지 점검
- 수정된 EmaCrossStrategy, DonchianBreakoutStrategy에 파라미터 최적화 단위 테스트 추가
- optimize_ema_cross(), optimize_donchian() 통합 테스트: 다른 params 조합이 다른 결과를 내는지 검증

#### C(데이터): 합성 데이터 품질 개선
- 현재 GBM 합성 데이터로는 전략 차별화 불가 (모두 FAIL)
- `make_synthetic_data()` 개선: 트렌드/레인지/변동성 전환 구간 포함하는 현실적 합성 데이터

#### F(리서치): IS 최적화 효과 측정 방법 설계
- factory 버그 수정 후 IS Sharpe가 실제로 개선되었는지 단위 검증
- 파라미터별 IS/OOS Sharpe 분포 로깅 추가

### ✅ Cycle 184 완료 사항

#### D(ML): WalkForwardOptimizer factory 버그 수정 ✅ COMPLETE
- EmaCrossStrategy `__init__(fast_span=20, slow_span=50)` + `_get_ema_values()` 동적 계산
- DonchianBreakoutStrategy `__init__(channel_period=20)` + `_get_channel_values()` 동적 계산
- optimize_ema_cross(), optimize_donchian() factory 함수가 실제로 params 주입

#### D(ML): OOS Sharpe std 필터 (RollingOOSValidator) ✅ COMPLETE
- BundleOOSResult.oos_sharpe_std 필드 추가
- RollingOOSValidator.OOS_SHARPE_STD_MAX = 1.5
- validate() std > 1.5이면 FAIL 처리

#### E(실행): 파라미터 완화 ✅ COMPLETE
- volume_breakout: ATR 0.3~5.0 → 0.1~10.0
- dema_cross: 거리 필터 1.0% → 0.5%
- price_cluster: threshold 0.2% → 0.5%

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

**상태**: Cycle 184 완료 → Cycle 185 A(품질/IS Sharpe 2.5 기준) + C(합성 데이터 개선) + F(IS 최적화 효과 측정)
**최우선 과제**: IS Sharpe >= 2.5 전략 subset 재검증 + 합성 데이터 현실성 개선
