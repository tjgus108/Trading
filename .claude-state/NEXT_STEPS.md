# Next Steps

_Last updated: 2026-05-22 (Cycle 191 B+D+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 191 완료
- 191 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)** 패턴 ✅
- 다음 Cycle 192: **192 mod 5 = 2 → E(실행) + A(품질) + F(리서치)**

### 🔥 Cycle 191 주요 성과
- **VolTargeting EWMA**: vol_method="ewma" 옵션으로 레짐 전환에 빠른 반응
- **PerformanceTracker 타임스탬프**: record_trade()에 timestamp + get_hourly_pnl() 시간별 PnL 버킷
- **WF fold time-decay**: fold_decay 파라미터로 최근 fold에 지수적 가중치 부여
- **리서치**: 90%+ 학술 전략 실전 FAIL 확인, AlgoXpert IS→WFA→OOS 프로토콜이 우리 방향과 일치

### 🔥 Cycle 190 주요 성과
- **팩토리 함수 버그 수정**: optimize_* 8개 함수 → plateau_pct kwarg 추가
- **볼륨 단위 정규화**: DataFeed에 volume_unit 파라미터 + volume_quote 컬럼
- **MDD 경계 케이스**: 3개 테스트 추가 + paper_simulation.py 버그 수정

### 🔥 Cycle 189 주요 성과
- **플래토 룰**: WalkForwardOptimizer에 plateau_pct=0.9 추가 — IS 최고 Sharpe 90% 이상 파라미터 중 중간값 선택
- **PaperTrader MDD**: equity_history + _calculate_max_drawdown() + get_summary()에 max_drawdown_pct 추가

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단 (원격 사이클에서는 합성 SIM만 가능)
- DataFeed.DEFAULT_FALLBACK_EXCHANGES = ["binance", "okx", "bitget"] 준비됨
- 로컬 환경에서 `DataFeed(connector, fallback_exchange_ids=DataFeed.DEFAULT_FALLBACK_EXCHANGES)` 활성화

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

### 🎯 Cycle 192 권장 작업 (192 mod 5 = 2 → E(실행) + A(품질) + F(리서치))

#### E(실행): Paper Trading 검증 + TWAP 개선
- PaperTrader에 VolTargeting(EWMA) 통합 테스트
- fold_decay 적용한 WF 결과로 paper trading 전략 선택
- TWAP 실행기 슬리피지 모델 검증

#### A(품질): 테스트 커버리지 향상
- VolTargeting EWMA + PerformanceTracker 통합 테스트
- WalkForward fold_decay + plateau_pct 복합 효과 검증
- MDD 계산 경계 케이스 추가

#### F(리서치): 실데이터 WF 최적화 전략 리서치
- fold_decay 효과 실데이터 검증 — 최근 fold 가중치가 OOS 개선하는지 확인
- EWMA vol vs simple vol 실데이터 비교
- AlgoXpert IS→WFA→OOS 프로토콜 상세 분석

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

**상태**: Cycle 191 완료 → Cycle 192 E(실행) + A(품질) + F(리서치)
**최우선 과제**: 로컬 환경에서 DataFeed fallback 활성화 → WF 파라미터 최적화 + 실데이터 조합으로 OOS PASS 전략 발굴

### ✅ Cycle 187 완료 사항

#### CircuitBreaker: 급속 가격 하락 감지 추가 ✅ COMPLETE
- `record_price(close_price)` 메서드 추가: 캔들 확정 시 가격 기록 + 쿨다운 tick
- `_check_rapid_decline()` 내부 메서드: 최근 N캔들 내 하락 ≥ rapid_decline_pct 감지
- 파라미터 (기본값): `rapid_decline_pct=0.05`, `rapid_decline_window=5`, `rapid_decline_cooldown_periods=30`
- check() 우선순위: 플래시 크래시 → 낙폭 → 연속손실 쿨다운 → **급속 하락** → 거래 횟수 → ATR/상관
- `reset_daily()` / `reset_all()` 에 rapid_decline 상태 초기화 포함
- `to_dict()` / `from_dict()` 직렬화 지원
- `rapid_decline_cooldown` 프로퍼티 추가
- 테스트 8개 추가 (total 110 → 110 passed, 신규 포함)

#### DrawdownMonitor: 4단계 임계값 유지 (변경 불필요) ✅
- 현재 임계값: WARN=5%, BLOCK=10%, LIQUIDATE=15%, HALT=20%
- 2026 기관 참여 확대 환경에서도 적절 — 이유:
  1. HIGH_VOL 레짐 시 daily_limit을 2%로 자동 강화하는 `set_regime()` 이미 구현됨
  2. 레짐별 cooldown 배수(HIGH_VOL×2.0, TREND_DOWN×1.5)로 시장 구조 변화 반영
  3. 5%→10%→15%→20% 4단계 누진 구조는 급격한 시장 충격에 충분히 대응 가능
  4. 임계값 하향 시 오히려 정상 변동성에서 과도한 false positive 위험

#### D(ML): Parameter Stability CV + Stability Penalty ✅ COMPLETE
- WalkForwardResult.param_stability_cv: fold간 파라미터 CV = std/|mean|
- CV > 0.5 WARNING 로그
- 목적함수: Score = Sharpe - λ*CV (stability_lambda=0.5)
- 테스트 27/27 통과

#### F(리서치): 대안 데이터소스 + 합성데이터 한계 ✅ COMPLETE
- Binance: 1년치 8760봉 fetch 성공 (2.36s, public API)
- OKX: 1년치 fetch 성공 (5.48s)
- 합성 데이터 개선: Jump-Diffusion + Regime-Switching 혼합 권장
- Survivorship bias: 상장폐지 코인 제외 시 4배 과대평가

#### SIM: 대안 거래소 fetch 테스트 ✅ COMPLETE
- Binance/OKX/Bitget 모두 SSL 에러 없이 접근 성공
- DataFeed fallback 구현으로 실데이터 병목 해소 가능

**상태**: Cycle 187 전체 완료
