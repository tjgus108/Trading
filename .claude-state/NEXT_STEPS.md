# Next Steps

_Last updated: 2026-05-23 (Cycle 199 D+E+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 199 완료
- 199 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 200: **200 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 199 주요 성과
- **E1 버그 수정**: PaperTrader.execute_signal() 잔액 사전 체크를 타임아웃 전으로 이동 → test_buy_insufficient_balance_rejected 비결정적 실패 수정
- **E2 기능 추가**: PaperTrader.check_sl_tp() — SL/TP 도달 시 자동 SELL 실행
- **D1 검증 강화**: WalkForwardOptimizer fold_decay 음수 ValueError 추가 (권장 범위 0.0~1.0 명시)
- **테스트 18개 추가**: fold_decay 범위 검증, DualGateADWIN cooldown 비교, PaperTrader SL/TP 8개

### 🎯 Cycle 200 권장 작업 (200 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): Quality Assurance
- `BacktestEngine.run()` 엣지 케이스 검토: 거래 0건 전략의 Sharpe/PF 반환 값 일관성
- QUALITY_AUDIT.csv 재감사: `value_area`, `wick_reversal`의 IS Sharpe 수치 재확인
  (IS Sharpe 높지만 OOS 전부 FAIL → IS 과최적화 가능성)
- `elder_impulse` fold 1 PASS 구간 분석: 어느 시장 상황인지 확인 (상승 추세 구간 가능성)

#### C(데이터): Data & Infrastructure
- `DataFeed.fetch()` 캐시 TTL 정책 검토: 합성 fallback 시 캐시 갱신 여부
- `RegimeAwareFeatureBuilder` 피처 중요도 출력 (합성 데이터 기준 feature_importances_)
- `narrow_range` 신호 완화: NR7 → NR4 전환 시 4h fold당 예상 거래 수 계산 (코드 분석)

#### F(리서치): SIM 결과 기반
- **elder_impulse + wick_reversal**: 두 전략이 fold 1 동시 PASS → 동일 구간 → 공통 특성 분석
- **narrow_range 0거래**: NR7 조건이 4h 합성 데이터에서 왜 미트리거인지 코드 분석
- **합성 vs 실데이터 갭**: IS Sharpe 음수(합성)이지만 IS Sharpe 양수(실데이터) 현상 원인 분석

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
