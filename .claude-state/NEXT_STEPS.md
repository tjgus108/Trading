# Next Steps

_Last updated: 2026-05-21 (Cycle 185 A+C+F+SIM + D+E+F+SIM 양쪽 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 185 완료
- 185 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)** + **D(ML) + E(실행) + F(리서치)** 양쪽 세션 완료 ✅
- 다음 Cycle 186: **186 mod 5 = 1 → B(리스크) + D(ML) + F(리서치)**

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (지속)

**Cycle 185 시뮬레이션 결과 (Synthetic data):**
- paper_simulation (1h, BTC, 22 strategies, 2 windows): 0/22 PASS
- bundle_oos (4h, BTC/USDT, 5 strategies, 9 folds): 0/5 PASS
- ⚠️ Bybit API SSL 차단으로 합성 데이터만 사용. 실제 데이터 결과 아님.
- OOS std 필터: 5/5 전략 std 3.16~6.15 > 1.5 (불안정 필터 동작)

### 🎯 Cycle 186 권장 작업 (186 mod 5 = 1 → B+D+F)

#### B(리스크): DrawdownMonitor + CircuitBreaker 재검토
- DrawdownMonitor.check() 현재 임계값 적절한지 검토
- CircuitBreaker 룰: 연속 손실 N회 → 강제 중단 로직 확인
- kelly_sizer.py: adjust_for_regime() 최신 레짐 기준 검토

#### D(ML): IS 최적화 효과 실질 검증
- 새 make_synthetic_data() (트렌드/레인지/변동성 구간 포함)로 IS 최적화 효과 측정
- optimize_ema_cross()의 last_is_sharpe_dist 확인: 파라미터별 IS Sharpe 분포가 실제로 다른지
- IS 최적 파라미터 ≠ 기본값인 경우 발생 비율 측정
- factory 수정 효과 검증: run_bundle_oos.py 재실행하여 OOS 재검증

#### F(리서치): CPCV 적용 가능성 검토 + param stability
- Combinatorial Purged Cross-Validation (CPCV) — Lopez de Prado 기법
- 현재 12개월 데이터로 n=4 그룹 → C(4,2)=6 경로 가능
- walk_forward.py에 CPCV 모드 추가 고려
- fold별 param stability(CV) 측정 → stability penalty 적용 (Freqtrade Hyperopt 패턴 참고)

### ✅ Cycle 185 완료 사항 (양쪽 세션 통합)

#### A(품질): IS Sharpe >= 2.5 재검증 ✅ COMPLETE
- QUALITY_AUDIT.csv: 22개 PASS 전략 모두 IS Sharpe >= 2.5 (최저 2.98)
- DSR 기준 상향 불필요 — 현재 선별 기준으로 충분

#### A(품질): 파라미터 최적화 단위 테스트 4개 추가 ✅ COMPLETE
- test_optimize_ema_cross_uses_params()
- test_optimize_donchian_uses_params()
- test_ema_cross_dynamic_params()
- test_donchian_dynamic_params()
- make_df() 확장: rsi14, vwap, ema9/20/21/50, volume, donchian 컬럼

#### C(데이터): make_synthetic_data() 레짐 개선 ✅ COMPLETE
- 트렌드/레인지/변동성 폭발 블록 포함
- GARCH-like volatility clustering
- 레짐 지속성 강화, 볼륨↔변동성 상관관계 개선

#### D(ML): WalkForwardOptimizer factory 함수 수정 ✅ COMPLETE (Cycle 185)
- `EmaCrossStrategy(fast_span, slow_span)`, `DonchianBreakoutStrategy(channel_period)` __init__ 추가
- `optimize_ema_cross`, `optimize_donchian` factory가 params를 실제로 생성자에 전달
- 전략이 params 기반으로 EMA/Donchian 채널을 동적 재계산

#### D(ML): OOS Sharpe 표준편차 필터 추가 ✅ COMPLETE (Cycle 185)
- `RollingOOSValidator.validate()`: fold별 OOS Sharpe std 계산
- `oos_sharpe_std > 1.5`이면 `all_passed=False` + fail_reason 추가
- `BundleOOSResult.oos_sharpe_std` 필드 추가 (summary()에도 출력)

#### E(실행): 거래 0건 전략 3개 파라미터 완화 ✅ COMPLETE (Cycle 185)
- volume_breakout: ATR 필터 범위 확대 (0.3~5.0 → 0.1~10.0) ✅
- dema_cross: 거리 필터 완화 (1% → 0.5%) ✅
- price_cluster: threshold 확대 (0.2% → 0.5%) ✅
- 테스트 40/40 통과. 완화 후 OOS walk-forward 재검증 필요

#### F(리서치): IS 최적화 효과 측정 메커니즘 ✅ COMPLETE
- walk_forward.py: 파라미터별 IS Sharpe 분포 로깅 (param_is_sharpes dict)
- WalkForwardResult.last_is_sharpe_dist 필드 추가
- 윈도우별 IS/OOS gap 로깅

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

**상태**: Cycle 185 완료 → Cycle 186 B(리스크) + D(ML/IS최적화효과) + F(CPCV리서치+param stability)
**최우선 과제**: IS 최적화 효과 실질 검증 + DrawdownMonitor/CircuitBreaker 재검토
