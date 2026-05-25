# Next Steps

_Last updated: 2026-05-25 (Cycle 207 B+D+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 207 완료
- 207 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅
- 다음 Cycle 208: **208 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 207 주요 성과
- **B1**: config.yaml `max_consecutive_losses: 5 → 4` (DrawdownMonitor threshold 3과 불일치 완화)
- **B2**: `portfolio_optimizer._parametric_var_cvar` scipy fallback 추가 (numpy 기반 대체)
- **D1**: `FeatureBuilder.build_with_feature_selection()` 추가 — MLSignalGenerator 피처 pruning 연계
- **F**: `run_bundle_oos.py --min-trades` CLI 옵션 추가 (기본 3, 저빈도 전략 분석 시 2 사용)
- **SIM**: narrow_range ATR 완화 효과 확인 (fold 1, 6 PASS → 이전 0 PASS에서 개선)

### 🎯 Cycle 208 권장 작업 (208 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): Data & Infrastructure
- DataFeed WebSocket 안정성 점검: `src/data/feed.py` recovery_timeout=300s 적용 후 안정성 확인
- DataFeed 캐시 전략: 동일 심볼/타임프레임 재요청 시 메모리 캐시 TTL 활용 여부 확인
- `src/data/` 모듈 전체 임포트 에러 없는지 확인 (ccxt 없는 환경에서도 graceful)

#### B(리스크): Risk Management
- DrawdownMonitor `streak_recovery_grace_seconds` live config 활성화 확인
  - `config/config.yaml`에 `streak_recovery_grace_seconds: 14400` 추가 고려
- CircuitBreaker `max_consecutive_losses=4` (Cycle 207 적용) 동작 검증
  - DrawdownMonitor `loss_streak_threshold=3`: 3회 손실 → 50% 축소
  - CircuitBreaker `max_consecutive_losses=4`: 4회 손실 → 쿨다운
  - 두 모듈이 순차적으로 단계적 차단 적용됨 → 의도된 설계 확인
- VaR/CVaR scipy fallback 검증: scipy 없는 환경 시뮬레이션 테스트

#### F(리서치): SIM 결과 기반
- **narrow_range 2 PASS fold 심층 분석**:
  - fold 1 (2022년 중반?): OOS=1.422, trades=4, PF=1.560 → 어떤 시장 환경?
  - fold 6 (2023-24년?): OOS=2.809, trades=4, PF=2.268 → 유사 환경 탐색
  - 공통점 분석: 좁은 레인지 구간 특성 (ATR 낮은 구간)
- **--min-trades 2 옵션으로 narrow_range 재검증**:
  - `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --min-trades 2`
  - fold 3 (trades=2, OOS=5.980) 포함 시 효과 측정 — 단, 2-trade fold 신뢰도 낮음
- **value_area OOS Sharpe std=6.589 대응**:
  - std가 높은 원인: fold별 va_mult 최적값 달라짐
  - 다음 사이클에서 va_mult 고정값(예: 1.5 단일)으로 std 감소 여부 확인

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 207 / 합성 GBM 환경)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — GBM IS 음수 패턴 지속
- **narrow_range: ATR_THRESHOLD=0.90, VOL_SPIKE_MULT=1.0 → fold 1,6 PASS (진전)**
- value_area: fold 0,6 PASS (2 fold) — std=6.589 여전히 불안정
- elder_impulse: fold 1 PASS (OOS=3.794) — 3개 사이클 연속 동일 패턴

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS — GBM 한계 동일
- 상위: price_action_momentum(6.90), cmf(5.99), momentum_quality(5.64)
- elder_impulse: 1.32 Sharpe, 28 trades (안정적)

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
**narrow_range: Cycle 207에서 fold 1,6 PASS (합성 4h) → 실데이터 검증 우선 후보 추가됨.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 207 완료 → Cycle 208 C(데이터) + B(리스크) + F(리서치) 예정
**최우선 과제**: narrow_range --min-trades 2 검증 + elder_impulse/narrow_range 실데이터 OOS 검증
