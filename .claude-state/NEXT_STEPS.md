# Next Steps

_Last updated: 2026-05-24 (Cycle 204 D+E+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 204 완료
- 204 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅
- 다음 Cycle 205: **205 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)**

### 🔥 Cycle 204 주요 성과
- **D1 개선**: `run_bundle_oos.py` IS 음수 fold 자동 진단 섹션 추가
  - `format_is_diagnosis()` 함수 추가 → fold별 IS Sharpe 음수 비율 집계 + 진단 기호
  - IS 전부 음수 전략 자동 경고 → GBM 합성 데이터 vs 전략 미작동 구분 자동화
- **E1 개선**: `TWAPExecutor.estimate_slippage()` 기본값 0.00055로 조정
  - Bybit taker 0.055%와 PaperTrader fee_rate=0.00055 일관성 확보
  - 관련 테스트 `test_twap_slippage_default` 기대값 업데이트

### 🎯 Cycle 205 권장 작업 (205 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): Quality Assurance
- 전략 백테스트 품질 재검증
  - elder_impulse: IS 양수(fold2=0.685) → OOS 급락(-5.556) 이유 분석
    → BacktestEngine 단기 GBM spike 민감도 확인
  - value_area: va_mult 파라미터 범위 0.6~0.8 → 0.65~0.75 축소 검토 (WFE 개선 목적)
- 테스트 커버리지: `run_bundle_oos.py format_is_diagnosis()` 단위 테스트 추가

#### C(데이터): Data & Infrastructure
- narrow_range 4h 0 trades 문제: NarrowRange 전략 트리거 조건 확인
  - `src/strategy/narrow_range.py` NR7 lookback 파라미터 확인
  - backtest 파라미터 lookback=5 또는 1h/2h 타임프레임 변경 효과 측정
- DataFeed fallback SSL 재시도 (Cycle 203 추가) 동작 검증
  - 원격 환경 시뮬레이션 단위 테스트 추가

#### F(리서치): SIM 결과 기반
- **elder_impulse 실데이터 검증 우선**:
  - 로컬 환경에서 DataFeed fallback 활성화 → fold 1 패턴이 실데이터에서도 재현되는지 확인
  - IS=−2.859 → OOS=+3.794 (fold 1): GBM noise 우연인지 실패 사이클인지 판별
- value_area 상위 fold 분석: fold 0 (OOS=3.559, PF=3.148), fold 6 (OOS=9.516) 파라미터 공통점 탐색

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 204)

**Bundle OOS (4h) — 합성 데이터 (동일 패턴 지속):**
- 0/5 PASS — IS Sharpe 전부 음수 (GBM 랜덤워크) → 자동 진단 섹션으로 확인 가능
- cmf: ⚠️ IS 전부 음수 (9/9 fold) → GBM 합성 데이터 한계
- elder_impulse: ⚠️ IS 전부 음수 (8/9 fold), fold 1만 PASS (OOS=3.794)
- wick_reversal: ⚠️ IS 전부 음수 (9/9 fold), fold 1,8 PASS
- narrow_range: 0/9 trades (min_oos_trades=3 기준 전체 제외)
- value_area: OOS Sharpe std=6.589 (최대 불안정), 4 near-PASS fold

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

**상태**: Cycle 204 완료 → Cycle 205 A(품질) + C(데이터) + F(리서치) 예정
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → elder_impulse/wick_reversal 실데이터 OOS 검증
