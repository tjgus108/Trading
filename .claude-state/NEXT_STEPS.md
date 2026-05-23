# Next Steps

_Last updated: 2026-05-23 (Cycle 198 C+B+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 198 완료
- 198 mod 5 = 3 → **C(데이터) + B(리스크) + F(리서치)** 패턴 ✅
- 다음 Cycle 199: **199 mod 5 = 4 → D(ML) + E(실행) + F(리서치)**

### 🔥 Cycle 198 주요 성과
- **DataFeed exchange fallback 소진 후 stale cache**: fallback_exchange_ids 구성 시 오류 타입 무관하게 stale cache 시도 (primary + 모든 fallback 실패 케이스 대응)
- **CircuitBreaker 동시 발생 시나리오 3개**: rapid_decline + consecutive_losses, 쿨다운 만료 후 rapid_decline 이어받음, rapid_decline + ATR 급등 우선순위 확인
- **VolTargeting + DrawdownMonitor 결합 4개**: NORMAL/WARN/BLOCK_ENTRY 전 단계에서 MDD size_multiplier가 vol_adjusted에 정확히 곱해지는 것 검증

### 🎯 Cycle 199 권장 작업 (199 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML & Signals 개선
- `WalkForwardOptimizer` fold_decay 파라미터 범위 좁히기 (현재 0.5~1.0 → 0.7~1.0 검토)
- `RegimeAwareFeatureBuilder` 피처 중요도 분석 — 실데이터 없이 합성 데이터 기준이라도 feature_importances_ 출력
- `DualGateADWIN` retrain 트리거 임계값 조정 테스트

#### E(실행): Execution & Paper Trading
- `PaperTrader` 포지션 청산 조건 검증 (stop_loss, take_profit 가격 도달 시 확실히 청산)
- TWAP 실행기 슬리피지 모델 정확도 점검
- `ImplShortfall` 계산 로직 단위 테스트

#### F(리서치): 실 데이터 전략 검증 방법 연구
- **value_area 실데이터 OOS 검증 우선**: 합성 데이터에서 4/9 fold PASS → 실데이터 기준 가장 유망
- **narrow_range 신호 완화**: NR7 → NR4 전환 시 4h에서 거래 수 예측 (현재 0건)
- **elder_impulse fold 1 분석**: 특정 시장 상황에서만 OOS PASS → 레짐 필터 추가 검토

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 198)

**Bundle OOS (4h) — 합성 데이터:**
- 5/5 FAIL — IS Sharpe 전부 음수 (GBM 랜덤워크)
- narrow_range: 9 fold 전부 OOS 거래 0건 → 신호 조건 너무 엄격
- value_area: 4/9 PASS fold → 가장 안정적 (실데이터 검증 1순위)
- OOS Sharpe std 3~6 (매우 불안정) → 합성 데이터 한계

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS consistency — BTC=ETH=SOL 동일 패턴 (GBM 랜덤워크)
- 합성 데이터 IS Sharpe 높은 전략: cmf(5.99), price_action_momentum(6.90)
- **결론: 실제 Bybit 데이터 확보가 최우선 병목**

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
**value_area → 합성 4h OOS에서 4/9 PASS → 실데이터 검증 최우선.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 198 완료 → Cycle 199 D(ML) + E(실행) + F(리서치)
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → value_area 실데이터 OOS 검증
