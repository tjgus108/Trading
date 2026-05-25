# Next Steps

_Last updated: 2026-05-25 (Cycle 208 C+B+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 208 완료
- 208 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** 패턴 ✅
- 다음 Cycle 209: **209 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 208 주요 성과
- **C1**: `feed.py` scipy 최상위 임포트 → graceful fallback (numpy 기반 kurtosis/skewness)
- **B1**: `DrawdownMonitor.to_dict()` streak_recovery_grace_seconds 누락 버그 수정
- **B2**: `config/config.yaml` `streak_recovery_grace_seconds: 14400` 활성화
- **SIM**: narrow_range 3 PASS fold (fold 1,3,6) → 이전 2 PASS에서 개선

### 🎯 Cycle 209 권장 작업 (209 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML & Signals
- RF/ML 모델 피처 중요도 분석: `src/ml/features.py` build_with_feature_selection() 활용
  - MLSignalGenerator 낮은 중요도 피처 제거 후 성능 변화 측정
- Walk-Forward 통합 확인: `src/backtest/walk_forward.py` 토너먼트 파이프라인 연동
  - `src/backtest/tournament.py` 또는 관련 파일에서 walk_forward 호출 여부 확인
- `src/ml/` 모듈 전체 임포트 에러 없는지 검증

#### E(실행): Execution & Paper Trading
- Paper Trading 모드 검증: `src/exchange/` 연결 로직 점검
- TWAP 실행기: `src/execution/` 또는 관련 파일 확인
- 슬리피지 모델 정확도 점검

#### F(리서치): SIM 결과 기반
- **narrow_range 3 PASS fold 패턴 분석** (Cycle 208 기준):
  - fold 1: IS=-1.263, OOS=1.422, trades=4, PF=1.560 → 어떤 GBM 특성?
  - fold 3: IS=-2.002, OOS=5.980, trades=2, PF=inf → 저거래 fold (신뢰도 낮음)
  - fold 6: IS=0.735, OOS=2.809, trades=4, PF=2.268 → ATR 낮은 구간 특성
  - 공통점: IS Sharpe 낮거나 음수 → narrow_range의 IS 최적화 보다 OOS 우연성 높음
- **value_area va_mult 고정값 실험**:
  - OOS std=6.589 해결 방안: va_mult 단일 값(1.5) 고정 후 std 감소 확인
  - fold 0,4,6,8 PASS (4 fold) — 다음 사이클에서 파라미터 좁히기 시도
- **wick_reversal fold 1 PASS 분석**:
  - fold 1: IS=-5.060(음수!), OOS=4.832 — IS 음수에서 OOS 양수: 운 또는 레짐 전환

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 208 / 합성 GBM 환경)

**Bundle OOS (4h) — 합성 데이터:**
- 0/5 PASS — GBM IS 음수 패턴 지속
- **narrow_range: fold 1,3,6 PASS (3 fold) → 이전 2 fold에서 개선**
- value_area: fold 0,4,6,8 PASS (4 fold) — std=6.589 불안정
- elder_impulse: fold 1 PASS (OOS=3.794) — 4 사이클 연속 동일 fold PASS
- wick_reversal: fold 1,8 PASS — 이전 대비 fold 수 증가

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
**narrow_range: Cycle 208에서 fold 1,3,6 PASS (합성 4h) → 실데이터 검증 우선 후보.**
**value_area: fold 0,4,6,8 PASS (4 fold) — va_mult 고정 실험 후 결론.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 208 완료 → Cycle 209 D(ML) + E(실행) + F(리서치) 예정
**최우선 과제**: narrow_range 실데이터 OOS 검증 + value_area va_mult 고정 실험
