# Next Steps

_Last updated: 2026-05-24 (Cycle 205 A+C+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 205 완료
- 205 mod 5 = 0 → **A(품질) + C(데이터) + F(리서치)** 패턴 ✅
- 다음 Cycle 206: **206 mod 5 = 1 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 205 주요 성과
- **A1 버그 수정**: `paper_trader.py` SELL 포지션 없음 체크 → timeout 이전으로 이동
  - `test_sell_no_position_rejected` 간헐적 실패 영구 수정
- **A2 개선**: `DEFAULT_GRIDS` value_area va_mult 범위 축소 [0.6,0.7,0.8]→[0.65,0.70,0.75]
  - OOS Sharpe std 6.589 완화 목적 (실데이터 검증 필요)
- **A3 개선**: `NarrowRangeStrategy` nr_lookback 파라미터화 (기본 5, 이전 하드코딩 7)
  - `DEFAULT_GRIDS` narrow_range 추가 + `optimize_narrow_range()` 함수
  - 4h OOS 거래 수 fold 6: 1→2건 (min_oos_trades=3 아직 미달)
- **C1 테스트**: `test_feed_error_handling.py` SSL retry 3개 단위 테스트 추가

### 🎯 Cycle 206 권장 작업 (206 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk Management
- DrawdownMonitor.get_size_multiplier() — streak cooldown 로직 재검토
  - consecutive_losses 리셋 시점 조정: 실적 기반 vs. 시간 기반 하이브리드 검토
- KellySizer max_kelly 파라미터: 기본값 0.25 → 0.20 보수화 검토
  - Sharpe std가 높은 전략군 (value_area std=6.589) 대상 케어 필요
- CircuitBreaker recovery_timeout=60s → 300s 연장: API 재시도 폭주 방지

#### D(ML): ML & Signals
- RF 모델 피처 중요도 분석 (`src/ml/` 아래 모델 파일 확인)
  - 낮은 기여도 피처 제거 → 모델 경량화 + 과적합 방지
- 앙상블 가중치 정기 업데이트: SIM 결과 기반 전략별 가중치 재조정

#### F(리서치): SIM 결과 기반
- **narrow_range 신호 조건 완화 검토**:
  - ATR_THRESHOLD 0.85 → 0.90 (더 여유로운 ATR 수축 조건)
  - VOL_SPIKE_MULT 1.2 → 1.0 (거래량 급증 조건 완화)
  - 변경 전 단위 테스트로 신호 빈도 측정 필수
- **elder_impulse OOS std=4.099 원인 분석**:
  - fold 1 (OOS=3.794) vs fold 2 (OOS=-5.556) 차이: GBM seed 구간 특성
  - 실데이터 검증 우선순위 유지

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 205 / 합성 GBM 환경)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — GBM IS 음수 패턴 지속
- narrow_range: nr_lookback=5로도 min_oos_trades=3 미달
  → ATR_THRESHOLD 완화(0.85→0.90) 또는 min_oos_trades 2 하향 검토
- value_area: OOS Sharpe std=6.589 (최대 불안정), va_mult 범위 축소 적용됨 (실데이터 효과 미확인)
- elder_impulse: fold 1 PASS (OOS=3.794) — 실데이터 PASS 후보

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS — GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- elder_impulse: avg Sharpe=1.32, 28 trades — 22개 중 상대적으로 거래 수 안정

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- _fetch_public_ohlcv SSL 재시도 추가됨 (Cycle 203), 단위 테스트 추가됨 (Cycle 205)
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
**elder_impulse fold 1 PASS (합성 4h) → 실데이터 검증 우선.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 205 완료 → Cycle 206 B(리스크) + D(ML) + F(리서치) 예정
**최우선 과제**: narrow_range ATR 조건 완화 + elder_impulse/wick_reversal 실데이터 OOS 검증
