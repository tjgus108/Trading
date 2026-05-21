# Next Steps

_Last updated: 2026-05-21 (Cycle 186 A+C+F+SIM 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 186 완료
- 186 mod 5 = 1 → **A(품질) + C(데이터) + F(리서치)** 패턴 ✅
- 다음 Cycle 187: **187 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)**

### ✅ Cycle 186 A(품질) 완료 사항

#### 파라미터 kwargs 수용 확장: 5개 전략 ✅ COMPLETE
1. **CMFStrategy**: `period`, `buy_thresh`, `sell_thresh`, `high_conf`, `vol_percentile` kwargs 추가
2. **WickReversalStrategy**: `min_wick_ratio`, `vol_mult`, `sma_period`, `trend_period` kwargs 추가
3. **ElderImpulseStrategy**: `ema_span`, `macd_fast`, `macd_slow`, `macd_signal`, `min_volatility` kwargs 추가
4. **ValueAreaStrategy**: `va_period`, `va_mult`, `ema_short`, `ema_long`, `min_breach` kwargs 추가
5. **FRAMAStrategy**: 기존 __init__ 유지 + `**kwargs` 추가

#### walk_forward.py 확장: 5개 전략 factory 함수 추가 ✅ COMPLETE
- DEFAULT_GRIDS에 5개 전략 파라미터 그리드 추가
- `optimize_cmf()`, `optimize_wick_reversal()`, `optimize_elder_impulse()`, `optimize_value_area()`, `optimize_frama()` factory 함수 구현
- 패턴: `EmaCrossStrategy(fast_span, slow_span)`, `DonchianBreakoutStrategy(channel_period)` 기존 패턴 동일 적용
- 테스트 80/80 통과 (CMF, WickReversal, ElderImpulse, ValueArea, FRAMA)

### ✅ Cycle 186 C(데이터) 완료 사항

#### Bybit API SSL 문제 대응 ✅ COMPLETE (connector.py)
- ccxt 초기화에 `verify=True` 추가 (SSL 인증서 검증 활성화)
- `aiohttp_trust_env=True` 추가 (HTTP_PROXY/HTTPS_PROXY 환경변수 지원)
- 네트워크 차단 환경에서 프록시 설정으로 연결 가능
- SSL 차단 시 `verify=False`로 변경 가능

#### DataFeed 캐시 효율성 개선 ✅ COMPLETE (feed.py)
- 캐시 키 정규화: 심볼을 대문자로 통일 (BTC/USDT == btc/usdt == Btc/Usdt)
- fetch() 메서드에 `symbol_normalized = symbol.upper()` 추가
- invalidate_cache() 메서드도 심볼 정규화 적용
- 테스트: 캐시 hit율 향상 확인 (3개 신규 테스트 통과, 기존 23개 테스트 모두 통과)
- 실무 환경에서 hit율 10~20% 향상 예상

### 🎯 Cycle 187 권장 작업 (187 mod 5 = 2 → B+D+F)

#### B(리스크): DrawdownMonitor + CircuitBreaker 재검토
- DrawdownMonitor.check() 현재 임계값 적절한지 검토
- CircuitBreaker 룰: AI 봇 군집매도 패턴 대응 (2026 리서치 결과)
- 플래시크래시 감지: 5분 내 5% 이상 하락 시 신규 진입 중단 로직

#### D(ML): 실제 데이터 확보 → OOS 재검증 (최우선)
- ⚠️ 합성 데이터에서는 IS Sharpe 자체가 음수 → 최적화 무의미 확인됨
- connector.py SSL 설정 수정 후 실제 Bybit 데이터 fetch 시도
- 실데이터 확보 시 7개 factory(EmaCross, Donchian, CMF, WickReversal, ElderImpulse, ValueArea, FRAMA) OOS 재검증
- fold별 param stability CV 측정 구현 (CV > 0.5 → fallback)

#### F(리서치): param stability 구현 검증 + CPCV 실용성
- CV = std(params) / mean(params), 임계값: < 0.3 안정, > 0.6 불안정
- Sharpe - λ*CV (λ=0.5~1.0) penalty 목적함수 통합 방법
- 90% plateau rule: IS 최고 Sharpe의 90% 이상 파라미터 범위 중간값 선택

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (합성 데이터 한계 확인)

**Cycle 186 SIM 결과:** factory 수정 후에도 0/5 PASS (변화 없음)
- IS Sharpe 자체가 음수(-6.5~2.3) → 합성 데이터에서는 최적화 신호 없음
- factory 수정은 올바르지만 합성 데이터 환경에서 효과 검증 불가
- **결론: 실제 Bybit 데이터 확보가 최우선 병목**

---

### ✅ 지난 사이클 완료 사항 (Cycle 185)

#### A(품질): IS Sharpe >= 2.5 재검증 ✅ COMPLETE
- QUALITY_AUDIT.csv: 22개 PASS 전략 모두 IS Sharpe >= 2.5 (최저 2.98)

#### A(품질): 파라미터 최적화 단위 테스트 4개 추가 ✅ COMPLETE
- test_optimize_ema_cross_uses_params()
- test_optimize_donchian_uses_params()
- test_ema_cross_dynamic_params()
- test_donchian_dynamic_params()

#### C(데이터): make_synthetic_data() 레짐 개선 ✅ COMPLETE
- 트렌드/레인지/변동성 폭발 블록 포함
- GARCH-like volatility clustering

#### D(ML): WalkForwardOptimizer factory 함수 수정 ✅ COMPLETE
- EmaCrossStrategy(fast_span, slow_span) → params 실제 전달
- DonchianBreakoutStrategy(channel_period) → params 실제 전달

#### D(ML): OOS Sharpe 표준편차 필터 추가 ✅ COMPLETE
- RollingOOSValidator.validate(): fold별 OOS Sharpe std 계산
- oos_sharpe_std > 1.5이면 FAIL

#### E(실행): 거래 0건 전략 3개 파라미터 완화 ✅ COMPLETE
- volume_breakout: ATR 필터 범위 확대
- dema_cross: 거리 필터 완화
- price_cluster: threshold 확대

#### F(리서치): IS 최적화 효과 측정 메커니즘 ✅ COMPLETE
- walk_forward.py: 파라미터별 IS Sharpe 분포 로깅
- WalkForwardResult.last_is_sharpe_dist 필드 추가

---

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

**상태**: Cycle 186 완료 → Cycle 187 B(리스크) + D(실데이터 OOS 재검증) + F(param stability 구현)
**최우선 과제**: 실제 Bybit 데이터 확보 → 7개 factory OOS 재검증 → PASS 전략 발굴
