# Next Steps

_Last updated: 2026-05-23 (Cycle 200 A+C+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 200 완료
- 200 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)** 패턴 ✅
- 다음 Cycle 201: **201 mod 5 = 1 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 200 주요 성과
- **A1 개선**: BacktestEngine.run() atr=0 신호 무시 추적 → fail_reasons에 "atr=0 skipped N signal(s)" 추가
  - narrow_range 4h 0거래 원인 진단 가능 (atr=0 vs 신호 자체 없음 구분)
  - 테스트 3개 추가
- **C1 개선**: DataFeed.fetch() stale cache fallback 성공 시 30초 TTL로 _cache 재저장
  - 거래소 다운 시 반복 retry 방지 (30초마다 1회만 재시도)

### 🎯 Cycle 201 권장 작업 (201 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk Management
- `DrawdownMonitor` 로직 검토: 현재 고점 기준 MDD 계산이 rolling vs. running 방식인지 확인
- `KellySizer` 분수 Kelly 적용 여부 확인: full Kelly는 과대 포지션 위험 — half Kelly (0.5x) 설정 검토
- `CircuitBreaker` 연속 손실 기반 룰: 현재 연속 손실 횟수 기준이 있는지, 없으면 추가 검토

#### D(ML): ML & Signals
- `WalkForwardOptimizer` fold_decay 0.7 기본값 재검토: 합성 데이터에서 fold 1 bias 줄이는 방향
- `DualGateADWINMonitor` retrain 빈도: cooldown=100 기준 실거래에서 적절한지 코드 분석
- `RegimeAwareFeatureBuilder` feature_importances_ 출력 (합성 데이터 기준 어느 피처가 높은지)

#### F(리서치): SIM 결과 기반
- **narrow_range NR4 전환 효과**: NR4 적용 시 4h fold당 예상 거래 수 분석 (NR7 조건 빈도 1/7 vs NR4 1/4)
- **elder_impulse + wick_reversal fold 1 동시 PASS**: fold 1 구간 공통 특성 → 실데이터 확보 시 우선 검증 후보
- **value_area OOS Sharpe std=6.589 지속**: 저거래(2-6 trades/fold) + GBM artifacts → 파라미터 조정 필요

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 199)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — IS Sharpe 전부 음수 (GBM 랜덤워크)
- elder_impulse: 1/9 PASS fold (fold 1) → 상승 추세 구간에서 작동
- wick_reversal: 2/9 PASS fold (fold 1, fold 8) → 비슷한 패턴
- narrow_range: 9/9 fold 거래 0건 → NR7 조건 4h에서 미트리거
- value_area: OOS Sharpe std 6.589 (최대 불안정), 저거래

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS consistency — 합성 GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- value_area: 평균 6거래 (0/8) — 1h에서도 신호 조건 엄격

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

**상태**: Cycle 199 완료 → Cycle 200 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → elder_impulse/wick_reversal 실데이터 OOS 검증
