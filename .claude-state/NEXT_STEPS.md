# Next Steps

_Last updated: 2026-05-25 (Cycle 208 C+B+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 208 완료
- 208 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** 패턴 ✅
- 다음 Cycle 209: **209 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 208 주요 성과
- **B1**: `config/config.yaml` + `src/config.py`: `streak_recovery_grace_seconds: 14400` 설정 지원 완성
  - DrawdownMonitor의 하이브리드 streak 회복 기능이 config에서 직접 제어 가능
- **C1**: `src/data/feed.py` `_evict_if_needed()`: stale_cache 크기 제한 추가 (무제한 증가 버그 수정)
- **SIM**: narrow_range 3 PASS fold (Cycle 207 2 PASS에서 진전), value_area 3 PASS fold

### 🎯 Cycle 209 권장 작업 (209 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML & Signals
- `src/ml/features.py` `build_with_feature_selection()` 실사용 확인
  - MLSignalGenerator와의 연동 테스트
  - 피처 중요도가 낮은 피처 5개 이상 제거 후 Sharpe 변화 확인
- RF 모델 재학습 여부 확인 (`scripts/train_ml.py` 실행 가능 환경 검증)
- 앙상블 가중치 (ML + 기술적 신호) 최적화 검토

#### E(실행): Execution
- TWAP executor 검증: `src/exchange/` 내 TWAP 구현 점검
- Paper trading 슬리피지 모델 정확도 점검
- `dry_run=true` 상태에서 주문 플로우 시뮬레이션 검증

#### F(리서치): SIM 결과 기반
- **narrow_range 3 PASS fold 심층 분석**:
  - fold 1 (OOS=1.422, 4 trades), fold 3 (OOS=5.980, 2 trades), fold 6 (OOS=2.809, 4 trades)
  - 공통점: ATR 낮은 구간 (좁은 레인지), IS Sharpe가 비교적 양수에 가까움
  - --min-trades 2 검증: `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --min-trades 2`
- **value_area 3 PASS fold 분석**:
  - fold 0(OOS=3.559), fold 4(OOS=1.056), fold 6(OOS=9.516) — std=6.589 여전히 불안정
  - va_mult 단일 고정값 시도: std 감소 효과 확인 목적
- **elder_impulse 4사이클 연속 fold 1 PASS**:
  - fold 1 기간 특성 분석: 2022년 중반 특정 시장 구조 (강한 추세 구간?)
  - 해당 구간 공통점 분석 → regime filter로 활성화 조건 검토

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 208 / 합성 GBM 환경)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — GBM IS 음수 패턴 지속
- **narrow_range: fold 1,3,6 PASS (3 PASS fold) → Cycle 207 대비 +1 개선**
- **value_area: fold 0,4,6 PASS (3 PASS fold) — std=6.589 불안정**
- elder_impulse: fold 1 PASS (OOS=3.794) — 4사이클 연속 동일
- wick_reversal: fold 1,8 PASS (2 PASS fold)
- cmf: 0 PASS fold (IS 전부 음수, GBM에서 역방향 신호)

**Paper SIM (1h) — 합성 데이터 (Cycle 207 결과):**
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
**narrow_range: Cycle 208에서 fold 1,3,6 PASS (합성 4h) → 최다 PASS fold 전략. 실데이터 검증 우선 후보.**
**value_area: Cycle 208에서 fold 0,4,6 PASS (합성 4h) → std 불안정, va_mult 고정 실험 필요.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 208 완료 → Cycle 209 D(ML) + E(실행) + F(리서치) 예정
**최우선 과제**: narrow_range --min-trades 2 검증 + elder_impulse/narrow_range 실데이터 OOS 검증
