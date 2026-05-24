# Next Steps

_Last updated: 2026-05-24 (Cycle 202 B+D+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 202 완료
- 202 mod 5 = 2 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅
- 다음 Cycle 203: **203 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)**

### 🔥 Cycle 202 주요 성과
- **D1 개선**: WalkForwardOptimizer.run() IS 전체 음수 fail_reason 추가
  - avg IS Sharpe < -0.5 시 "IS 전체 음수 — 전략 미작동 또는 합성 데이터(GBM)" 진단 메시지
  - GBM 합성 데이터 한계를 자동 감지하여 fail_reasons에 기록
- **D2 개선**: RegimeAwareFeatureBuilder.get_feature_importance() 진단 메서드 추가
  - RF 50트리 빠른 fit으로 레짐별 피처 중요도 dict 반환
  - 실데이터 검증 우선 피처 결정에 활용
- **B1 검증**: KellySizer ATR low 케이스 테스트 추가
  - `atr < target_atr` → factor=1.0 확대 없음 (의도적 보수적 설계) 확인
  - B2: `is_in_streak_cooldown()` 생산 코드 미사용 확인 (get_size_multiplier() 올바르게 사용)
  - B3: CircuitBreaker 우선순위 검토 — 현재 순서(플래시크래시>낙폭>쿨다운>급속하락) 적절

### 🎯 Cycle 203 권장 작업 (203 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): Data & Infrastructure
- `DataFeed.fetch_ohlcv()` retry backoff 파라미터 검토
  - 현재 SSL intercept 환경에서 bybit→binance→okx fallback 테스트
  - stale cache 30초 TTL 적용 후 효과 검증 (Cycle 200에서 수정됨)
- `OrderFlowAnalyzer` VPIN 계산 정확도 점검
  - 볼륨 버킷 사이즈가 고정값인지 동적인지 확인
  - 실데이터 없이 합성 데이터로 VPIN 결과가 의미있는지 검증

#### B(리스크): Risk Management 심화
- `DrawdownMonitor.is_in_streak_cooldown()` 시맨틱 명확화 검토
  - 현재: streak cooldown 만료 후에도 consecutive_losses>=threshold → get_size_multiplier() 0.5 유지
  - 고려: streak cooldown 만료 시 size 자동 복원 로직 추가 여부 (현재는 win 발생 시만 복원)
  - 결정: 현재 설계가 보수적으로 안전함 → 변경 불필요, 주석으로 문서화
- `CircuitBreaker` (manager.py 내장) vs. `CircuitBreaker` (circuit_breaker.py) 통합 고려
  - orchestrator.py는 manager.py CircuitBreaker 사용 (단순, tick_cooldown 없음)
  - circuit_breaker.py는 더 복잡하지만 미사용 상태 → 통합 또는 교체 검토

#### F(리서치): SIM 결과 기반
- **IS 전체 음수 패턴 분석 자동화**: 새 fail_reason을 활용해 Bundle OOS 보고서에서 "IS 전체 음수" 전략 목록 추출
- **get_feature_importance() 활용 계획**: 합성 데이터에서 return_1/return_3가 최고 중요도
  - 실데이터 확보 후 동일 방법론으로 피처 중요도 재측정 → 합성 vs 실데이터 비교 가능
- **value_area 파라미터 검토**: OOS std=6.589 지속 → 실데이터 없이는 개선 불가 확인
  - 로컬 환경에서 실데이터 fallback 활성화가 최우선 병목

### ⚠️ 핵심 문제: SIM 결과 패턴 (Cycle 202)

**Bundle OOS (4h) — 합성 데이터 (동일 패턴 지속):**
- 0/5 PASS — IS Sharpe 전부 음수 (GBM 랜덤워크) → 새 fail_reason으로 자동 진단됨
- elder_impulse: 1/9 fold PASS (fold 1) → seed=42 고유 패턴
- wick_reversal: 2/9 fold PASS (fold 1, fold 8 OOS PF=1.141)
- narrow_range: 9/9 fold 거래 0건 → NR7+ATR 4h 미트리거 지속
- value_area: OOS Sharpe std=6.589 (최대 불안정), 저거래

**Paper SIM (1h) — 합성 데이터:**
- 0/22 PASS consistency — GBM 한계 동일
- 상위 합성 성과: price_action_momentum (6.90), cmf (5.99)
- value_area: avg 6거래 (0/8) — 1h에서도 신호 조건 여전히 엄격

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
**elder_impulse fold 1 PASS (합성 4h), wick_reversal fold 1,8 PASS → 실데이터 검증 우선.**

---

### 🔧 /schedule 원격 에이전트 설정됨
- 5시간마다 자동 실행 (UTC 0/5/10/15/20시)
- 루틴 ID: trig_0145pyi9PxaqL9fbfd25nzEL

---

**상태**: Cycle 202 완료 → Cycle 203 C(데이터) + B(리스크) + F(리서치) 예정
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → elder_impulse/wick_reversal 실데이터 OOS 검증
