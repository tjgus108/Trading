# Next Steps

_Last updated: 2026-05-21 (Cycle 186 C 데이터 작업 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 186 완료 (A + C 완료)
- 186 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)**
- A(품질): 5개 전략 kwargs 수용 + walk_forward factory ✅
- C(데이터): Bybit API SSL 문제 대응 + 캐시 효율성 개선 ✅

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

### 🎯 Cycle 186 B+D+F 권장 작업

#### B(리스크): DrawdownMonitor + CircuitBreaker 재검토
- DrawdownMonitor.check() 현재 임계값 적절한지 검토
- CircuitBreaker 룰: 연속 손실 N회 → 강제 중단 로직 확인
- kelly_sizer.py: adjust_for_regime() 최신 레짐 기준 검토

#### D(ML): IS 최적화 효과 실질 검증 + OOS 재검증
- 새 make_synthetic_data() (트렌드/레인지/변동성 구간 포함)로 IS 최적화 효과 측정
- **이제 5개 전략 factory 완성 → run_bundle_oos.py 재실행으로 OOS 재검증 가능**
  - optimize_ema_cross(), optimize_donchian(), optimize_funding_rate() (기존)
  - optimize_cmf(), optimize_wick_reversal(), optimize_elder_impulse(), optimize_value_area(), optimize_frama() (신규)
- optimize_ema_cross()의 last_is_sharpe_dist 확인: 파라미터별 IS Sharpe 분포 검증
- factory 수정 효과: 5개 전략 OOS Sharpe 개선율 측정

#### F(리서치): CPCV 적용 가능성 검토 + param stability
- Combinatorial Purged Cross-Validation (CPCV) — Lopez de Prado 기법
- 현재 12개월 데이터로 n=4 그룹 → C(4,2)=6 경로 가능
- walk_forward.py에 CPCV 모드 추가 고려
- fold별 param stability(CV) 측정 → stability penalty 적용 (Freqtrade Hyperopt 패턴 참고)

### ⚠️ 핵심 문제: 전략 전부 OOS FAIL (Cycle 185 미해결)

**Cycle 185 시뮬레이션 결과 (Synthetic data):**
- paper_simulation (1h, BTC, 22 strategies, 2 windows): 0/22 PASS
- bundle_oos (4h, BTC/USDT, 5 strategies, 9 folds): 0/5 PASS
- ⚠️ Bybit API SSL 차단으로 합성 데이터만 사용. 실제 데이터 결과 아님.
- OOS std 필터: 5/5 전략 std 3.16~6.15 > 1.5 (불안정 필터 동작)

**이번 Cycle 186 D(ML)에서 5개 신규 factory 사용 OOS 재검증 추진.**

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

**상태**: Cycle 186 A(품질) 완료 → Cycle 186 B(리스크) + D(ML/OOS재검증) + F(CPCV리서치+param stability)
**최우선 과제**: 5개 신규 factory 사용 OOS 재검증 + DrawdownMonitor/CircuitBreaker 재검토
