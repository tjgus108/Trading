# Next Steps

_Last updated: 2026-05-25 (Cycle 208 D+E+SIM+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 208 완료
- 208 mod 5 = 3 → **D(ML) + E(실행) + F(리서치)** 패턴 (로컬 세션)
- 다음 Cycle 209: **209 mod 5 = 4 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 208 주요 성과 (로컬)
- **ML 추론 벤치마크**: predict() 호출마다 latency 추적, benchmark_stats() p50/p95/p99
- **OnChainFeatureStub**: exchange_netflow, sopr, defi_tvl 합성 폴백 인터페이스
- **PaperTrader KellySizer 통합**: BUY→compute_dynamic(), SELL→record_trade() 자동
- **Tiered Slippage**: BTC/ETH 0.05%, SOL/BNB 0.2%, 기타 1.0% (리서치 수치 반영)
- **SIM 66개 전부 FAIL**: value_area ETH Sharpe 0.92 최근접
- **리서치**: IS 승률 80%+는 과적합 신호, 파라미터 5개↑ OOS FAIL 필연

### 🔥 Cycle 207 주요 성과 (리모트)
- **B1**: config.yaml `max_consecutive_losses: 5 → 4`
- **B2**: portfolio_optimizer VaR/CVaR scipy fallback
- **D1**: FeatureBuilder.build_with_feature_selection() 추가
- **F**: run_bundle_oos.py --min-trades CLI 옵션
- **SIM**: narrow_range fold 1,6 PASS (ATR 완화 효과)

### 🎯 Cycle 209 권장 작업 (209 mod 5 = 4 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): Data & Infrastructure
- DataFeed WebSocket 안정성 점검: recovery_timeout=300s 적용 후 확인
- `src/data/` 모듈 전체 임포트 에러 없는지 확인 (ccxt 없는 환경에서도 graceful)
- 합성 데이터 seed 다양화: paper_simulation.py 심볼별 seed(42) 동일 문제

#### B(리스크): Risk Management
- DrawdownMonitor streak_recovery_grace_seconds live config 활성화 확인
- CircuitBreaker max_consecutive_losses=4 동작 검증
- VaR/CVaR scipy fallback 검증: scipy 없는 환경 시뮬레이션 테스트

#### F(리서치): SIM 결과 기반
- narrow_range 2 PASS fold 심층 분석 (fold 1,6 어떤 시장 환경?)
- --min-trades 2 옵션으로 narrow_range 재검증
- value_area OOS Sharpe std=6.589 대응 (va_mult 고정값 테스트)

### ⚠️ 핵심 문제
- 실데이터 PASS 전략 0개 — IS→OOS 괴리 심각
- 합성 데이터 동일 seed(42) → 3심볼 사실상 동일 데이터
- IS 승률 80%+는 과적합 역신호 (리서치 확인)

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

**상태**: Cycle 208 완료 → Cycle 209 C(데이터) + B(리스크) + F(리서치) 예정
**최우선 과제**: narrow_range/value_area 실데이터 OOS 검증 + 과적합 감사
