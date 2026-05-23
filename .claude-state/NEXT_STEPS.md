# Next Steps

_Last updated: 2026-05-23 (Cycle 201 B+D+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 201 완료
- 201 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅
- 다음 Cycle 202: **202 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)** (동일 카테고리 반복)

### 🔥 Cycle 201 주요 성과
- **B1 개선**: DrawdownMonitor.to_dict()/from_dict() `_equity_history` 직렬화 추가
  - 재시작 후 rolling_mdd() 항상 0 반환 버그 수정
  - 테스트 3개 추가 (to_dict 포함 확인, from_dict 복원 확인, 이전 버전 호환 확인)
- **D1 개선**: DualGateADWINMonitor.update() 배치 카운터 과잉 증가 버그 수정
  - N 피처 배치 업데이트 시 _samples_since_retrain이 N+1배 증가하던 문제
  - 10 피처 배치: cooldown=50이 실제 5 샘플 후 만료되던 것을 50 샘플로 정상화
  - 테스트 3개 추가
- **E(기존) 수정**: test_partial_fill_records_actual_quantity flaky 테스트 수정
  - initial_balance 50000 → 300000으로 증가 (4-5회 → 20회 유효 시도 보장)

### 🎯 Cycle 202 권장 작업 (202 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk Management 심화
- `KellySizer.compute()` ATR 제약 로직 검토: `atr_factor = min(target_atr/atr, 1.0)` → ATR 높을 때만 축소, 낮을 때 확대 없음 — 이게 맞는지 확인
- `DrawdownMonitor.is_in_streak_cooldown()` 반환 후 호출자가 실제로 거래를 막는지 확인: `get_size_multiplier()` 대신 직접 `is_in_streak_cooldown()` 쓰는 코드가 있는지 점검
- `CircuitBreaker.check()` 우선순위: 플래시크래시 → 낙폭 → 연속손실 쿨다운 → 급속하락 → 일일거래횟수 → ATR/상관. 이 순서가 적절한지 검토 (연속손실 쿨다운을 급속하락보다 먼저 체크하는 것이 맞는가?)

#### D(ML): ML & Signals 심화
- `WalkForwardOptimizer._optimize_in_sample()`: IS Sharpe 전체 음수 시 별도 fail reason 추가 검토
  - 현재: 플래토 룰이 `best_sharpe > 0` 조건으로 음수 IS 시 스킵됨 → 가장 덜 나쁜 파라미터 선택
  - 개선: avg_is_sharpe < -0.5 시 `"IS 전체 음수 — 전략 미작동 또는 합성 데이터"` fail_reason 추가
- `RegimeAwareFeatureBuilder`: 피처 중요도 진단 메서드 추가
  - `get_feature_importance(df)` → 빠른 RF fit으로 피처 중요도 dict 반환
  - 합성 데이터 GBM에서 어떤 피처가 최고 중요도인지 파악 → 실데이터 검증 우선순위 결정

#### F(리서치): SIM 결과 기반
- **value_area 파라미터 완화**: volume_factor_min, poc_diff_pct 등 완화 방향 검토 (합성 1h 기준 avg 6 trades → 15+ 목표)
- **wick_reversal fold 8 OOS PF=1.141**: 실데이터에서도 동일 패턴인지 확인 필요 — fold 8 기간 특성 분석
- **DualGateADWIN 버그 후속**: 실전 배포 시 피처 5-10개 사용하는 ML 파이프라인에서 cooldown이 올바르게 작동하는지 점검

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 201)

**Bundle OOS (4h) — 합성 데이터 (동일 패턴 지속):**
- 0/5 PASS — IS Sharpe 전부 음수 (GBM 랜덤워크) → 합성 데이터 한계
- elder_impulse: 1/9 fold PASS (fold 1) → seed=42 고유 패턴
- wick_reversal: 2/9 fold PASS (fold 1, fold 8 OOS PF=1.141)
- narrow_range: 9/9 fold 거래 0건 → NR7+ATR 4h 미트리거 지속
- value_area: OOS Sharpe std=6.589 (최대 불안정), 저거래

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS consistency — GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- value_area: avg 6거래 (0/8) — 1h에서도 신호 조건 여전히 엄격

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 `DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)` 활성화

### 📋 Paper Trading 자동화 판정 기준

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
**elder_impulse fold 1 PASS (합성 4h), wick_reversal fold 1,8 PASS → 실데이터 검증 우선.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 201 완료 → Cycle 202 B(리스크) + D(ML) + F(리서치) 예정
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → elder_impulse/wick_reversal 실데이터 OOS 검증
