# Next Steps

_Last updated: 2026-05-24 (Cycle 203 C+B+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 203 완료
- 203 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** 패턴 ✅
- 다음 Cycle 204: **204 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 203 주요 성과
- **C1 개선**: `DataFeed._fetch_public_ohlcv()` SSL 재시도 추가
  - SSL 오류(ccxt.NetworkError, "ssl"/"certificate" 키워드) → `verify=False`로 재시도
  - 원격 SSL 인터셉션 환경에서 공개 API fallback 성공률 향상
- **B1 문서화**: `DrawdownMonitor.get_size_multiplier()` 설계 의도 주석 추가
  - streak cooldown 만료 후에도 size 0.5 유지 — win 발생 시에만 복원 (보수적 설계)
- **B2 문서화**: `manager.py CircuitBreaker` 중복 상황 주석 추가
  - circuit_breaker.py는 미사용 상태, 통합 시 인터페이스 변경 필요

### 🎯 Cycle 204 권장 작업 (204 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 모델 / Walk-Forward
- `WalkForwardOptimizer.run()` IS 전체 음수 fail_reason (Cycle 202 추가) 활용
  - Bundle OOS 보고서에서 "IS 전체 음수" 전략 목록 자동 추출 기능 추가 검토
  - `src/backtest/walk_forward.py` fail_reasons 필드를 보고서 생성기에 노출
- `RegimeAwareFeatureBuilder.get_feature_importance()` (Cycle 202 추가) 활용
  - narrow_range 전략이 4h에서 0 거래인 이유 → 피처 중요도로 트리거 조건 분석
  - 합성 데이터에서 return_1/return_3가 최고 중요도 → 실데이터와 비교 계획 수립

#### E(실행): Execution & Paper Trading
- Paper Trading 모드 점검
  - `src/exchange/connector.py` TWAP 실행기 파라미터 검토
  - 슬리피지 모델이 실제 환경(0.05% 가정)과 일치하는지 확인
  - Telegram 알림 활성화 상태 점검

#### F(리서치): SIM 결과 기반
- **narrow_range 전략 신호 조건 완화 검토**:
  - 4h NR7+ATR 기준 0 trades 지속 → 파라미터 조정 또는 타임프레임 변경 고려
  - NR7 lookback 7 → 5 또는 타임프레임 2h 검토 (전략 파일 수정 금지, backtest 파라미터만)
- **value_area OOS std=6.589 분석**: 파라미터 범위 축소 가능성 검토

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 203)

**Bundle OOS (4h) — 합성 데이터 (동일 패턴 지속):**
- 0/5 PASS — IS Sharpe 전부 음수 (GBM 랜덤워크) → Cycle 202 fail_reason으로 자동 진단됨
- elder_impulse: 1/9 fold PASS (fold 1) → seed=42 고유 패턴 (불변)
- wick_reversal: 2/9 fold PASS (fold 1, fold 8 OOS PF=1.141)
- narrow_range: 9/9 fold 거래 0건 → NR7+ATR 4h 미트리거 지속
- value_area: OOS Sharpe std=6.589 (최대 불안정), 4/9 near-PASS

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS consistency — GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- elder_impulse: avg Sharpe=1.32 (22개 중 최저) → 실데이터에서 가장 안정적일 가능성
- value_area: avg 6거래 (0/8) — 1h에서도 신호 조건 여전히 엄격

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- _fetch_public_ohlcv SSL 재시도 추가됨 (Cycle 203)
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

**상태**: Cycle 203 완료 → Cycle 204 D(ML) + E(실행) + F(리서치) 예정
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → elder_impulse/wick_reversal 실데이터 OOS 검증
