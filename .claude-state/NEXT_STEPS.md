# Next Steps

_Last updated: 2026-05-24 (Cycle 206 B+D+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 206 완료
- 206 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅
- 다음 Cycle 207: **207 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)**

### 🔥 Cycle 206 주요 성과
- **B1**: KellySizer kelly_cap 0.25 → 0.20 (더 보수적 포지션 상한)
- **B2**: DrawdownMonitor `streak_recovery_grace_seconds` 하이브리드 회복 추가
  - 마지막 손실 이후 grace_seconds 경과 → consecutive_losses 자동 리셋
  - 기본값 0 (비활성), live 환경에서 streak_cooldown_seconds과 동일 값 권장
- **B3**: DataFeed CircuitBreaker `recovery_timeout` 60s → 300s (API 재시도 폭주 방지)
- **D1**: MLSignalGenerator `get_low_importance_features(threshold)` helper 추가
- **F**: narrow_range ATR_THRESHOLD 0.85→0.90, VOL_SPIKE_MULT 1.2→1.0 완화
  - 4h OOS 거래 0건 문제 완화 목적 → 다음 사이클 SIM에서 효과 확인 필요

### 🎯 Cycle 207 권장 작업 (207 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Risk Management (2회 연속 B)
- DrawdownMonitor `streak_recovery_grace_seconds` 실효성 검증
  - 기본값 0이므로 live config에 명시적 활성화 필요 (`config/` 파일 확인)
- VaR/CVaR 계산 정확도 검증: `src/risk/portfolio_optimizer.py` 코드 리뷰
  - 특히 normal distribution 가정 vs. fat-tail 보정 여부
- CircuitBreaker `max_consecutive_losses=5` → 4로 하향 검토
  - 현재 DrawdownMonitor와 CircuitBreaker 간 streak 임계값 불일치 (3 vs 5)

#### D(ML): ML & Signals
- MLSignalGenerator `get_low_importance_features()` 활용:
  - 실제 RF 모델 학습 후 threshold=0.01 피처 목록 추출
  - FeatureBuilder에서 해당 피처 제거 후 재학습 효과 측정
- HMM 레짐 감지 모델 (`src/ml/hmm_model.py`) 상태 확인
  - 현재 사용 중인지, 또는 단독 활성화 가능한지 확인

#### F(리서치): SIM 결과 기반
- **narrow_range ATR 완화 효과 측정**:
  - ATR_THRESHOLD 0.90으로 4h Bundle OOS 재실행하여 거래 수 변화 확인
  - 여전히 0건이면: min_oos_trades 2 하향 또는 nr_lookback 추가 완화 검토
- **elder_impulse fold 1 PASS 분석**:
  - fold 1 OOS 구간 특성 분석 (2024Q1 등 특정 시장 국면 대응 가능성)
  - 실데이터 검증 환경 준비 (로컬 환경에서 DataFeed fallback 활성화)

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 206 / 합성 GBM 환경)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — GBM IS 음수 패턴 지속
- narrow_range: ATR_THRESHOLD 0.90, VOL_SPIKE_MULT 1.0 적용됨 → 다음 SIM에서 거래 수 확인
- value_area: OOS Sharpe std=6.589 (va_mult 범위 축소 적용됨, 실데이터 효과 미확인)
- elder_impulse: fold 1 PASS (OOS=3.794) — 실데이터 PASS 후보

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS — GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- elder_impulse: avg Sharpe=1.32, 28 trades — 22개 중 상대적으로 안정

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

**상태**: Cycle 206 완료 → Cycle 207 B(리스크) + D(ML) + F(리서치) 예정
**최우선 과제**: narrow_range ATR 완화 효과 다음 SIM 확인 + elder_impulse 실데이터 OOS 검증
