# Next Steps

_Last updated: 2026-05-22 (Cycle 194 D+E+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 194 완료
- 194 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 195: **195 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 194 주요 성과
- **FeatureBuilder 온체인 피처**: exchange_netflow_norm + sopr_delta (선택적, Cycle 193 리서치 반영)
- **KellySizer(rolling) + VolTargeting(EWMA) + PaperTrader 통합 테스트 5개**: E2E 검증
- **RollingOOSValidator min_oos_trades=3**: 저거래 fold 집계 제외 → 더 정확한 전략 판정
- **BundleOOSResult summary() 버그 수정**: 중복 oos_sharpe_std 라인 제거
- **ML 트레이딩 프로덕션 배포 리서치**: PSI+Page-Hinkley drift 감지 + shadow→canary 파이프라인

### 🎯 Cycle 195 권장 작업 (195 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 테스트 커버리지 개선
- `RollingOOSValidator.validate()` 정상 PASS 경로 테스트 추가 (현재 FAIL 경로만 테스트됨)
- walk_forward.py `WalkForwardOptimizer`의 `fold_decay > 0` weighted_oos_sharpe E2E 검증
- feature_builder.py `RegimeAwareFeatureBuilder.build_with_cached_regime()` 테스트 추가

#### C(데이터): DataFeed + 온체인 피처 파이프라인
- DataFeed.fetch()가 반환하는 df에 `exchange_netflow`, `sopr` 컬럼 추가 인터페이스 설계
- CryptoQuant/Glassnode mock 데이터로 온체인 피처 E2E 테스트
- WebSocket ConnectionHealthMonitor stale 감지 → 자동 재연결 트리거 연동

#### F(리서치): Drift 감지 + 재학습 파이프라인
- Page-Hinkley / ADWIN을 현재 `drift_detector.py`와 비교 (기존 구현 강점/약점 분석)
- PSI(Population Stability Index) 계산 로직 설계 (피처 분포 변화 감지)
- shadow mode 실전 구현 아이디어: PaperTrader를 shadow로 사용, live 신호와 비교

### 🔥 Cycle 193 주요 성과
- **WebSocket ConnectionHealthMonitor**: stale 감지, 재연결 이력, health summary
- **KellySizer rolling win_rate**: record_trade() + compute_dynamic() — 실전 데이터 기반 자동 포지션 사이징
- **온체인 리서치**: Exchange Inflow 2σ→1주 하락 72%, 최우선 신호 3개 도출

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 `DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)` 활성화

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (합성 데이터 한계 확인)

**SIM 결과 패턴 (Cycle 194):**
- IS Sharpe 대부분 음수 → 합성 GBM 데이터에서 최적화 신호 없음
- OOS Sharpe std 3.1~6.2 → 불안정 (min_oos_trades 개선으로 일부 진단 개선됨)
- narrow_range: 거래 0건 fold 7/9 → 신호 조건 너무 엄격 (4h 타임프레임)
- **결론: 실제 Bybit 데이터 확보가 최우선 병목**

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

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 194 완료 → Cycle 195 A(품질) + C(데이터) + F(리서치)
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → WF 파라미터 최적화 + 실데이터 조합으로 OOS PASS 전략 발굴
