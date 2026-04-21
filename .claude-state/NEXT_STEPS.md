# Next Steps

_Last updated: 2026-04-22 (Cycle 179 D+E+F 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 179 완료
- 179 mod 5 = 4 → **D(ML) + E(실행) + F(리서치)** 패턴 ✅

### 🎯 Cycle 180 권장 작업 (180 mod 5 = 0 → A+C+F)

#### A(품질): 실데이터 OOS 실행
- `python3 scripts/run_bundle_oos.py`로 5-Bundle 실데이터 OOS 검증
- WFE ≥ 0.50, OOS Sharpe ≥ IS×0.60 확인
- 실패 전략 분석 및 파라미터 조정 여부 판단

#### C(데이터): DataFeed 안정성 + 실데이터 수집 검증
- Bybit 4h봉 데이터 수집 안정성 확인
- WebSocket reconnect/backoff 로직 검증
- 레짐 피처 실데이터 파이프라인 E2E 테스트

#### F(리서치): 포지션 동기화 + 장애 복구 패턴 심화
- API 장애 시 포지션 동기화 구현 방안 리서치
- systemd unit 파일 설계 리서치
- 실전 배포 전 보안 체크리스트 리서치

### ✅ Cycle 179 완료 사항

#### F(리서치): Paper Trading 자동화 + 봇 실패/성공 사례 ✅ COMPLETE
- 2025-2026 최신 봇 실패 사례: R² < 0.025 (백테스트 Sharpe가 실전 성과 예측 불가), 5월 플래시 크래시($20억 3분 매도), 4가지 구조적 실패 원인 정리
- Paper trading 권장 기간: 4~8주, 5% 급락 구간 포함 필수
- 자동 Go/No-Go 판정 기준: PF ≥ 1.4, MDD ≤ 15%, WFE ≥ 0.50, 주간 승률 ≥ 45%
- 스케줄러 비교: VPS → systemd 권장, Docker → Ofelia 권장
- API 장애 복구 3패턴: 지수 백오프 + Circuit Breaker + 포지션 동기화
- **결과물**: `.claude-state/RESEARCH_NOTES.md` Cycle 179 섹션 추가

#### D(ML): RegimeDetector → paper_trader 연결 ✅ COMPLETE
- `src/exchange/paper_trader.py`에 RegimeDetector/RegimeStrategyRouter/PerformanceMonitor 연결
- update_regime(df) 매 틱 호출, CRISIS 0.5x 자동 적용, 라우터 스킵 구현
- `tests/test_paper_trader_regime.py` — 23개 테스트 ALL PASS
- **다음**: 실데이터로 run_bundle_oos.py 실행 + 4주 paper trading 시작

#### E(실행): 5-Bundle OOS 인프라 + PerformanceMonitor 연결 ✅ COMPLETE
- `scripts/run_bundle_oos.py` -- 5-Bundle Rolling OOS 검증 실행 스크립트 생성
  - Bybit 실데이터 수집 (4h 기본, 페이지네이션), 5전략 순차 검증
  - 요약 테이블 + Fold별 상세 Markdown 리포트 자동 생성
  - 실행: `python3 scripts/run_bundle_oos.py [--symbol BTC/USDT] [--timeframe 4h]`
- `scripts/live_paper_trader.py` -- PerformanceMonitor 통합
  - `LivePerformanceTracker` + `PerformanceMonitor` 초기화
  - 거래 완료 시 `record_trade()` 자동 호출
  - 매 tick마다 `check_all()` -- Rolling PF/MDD/Sharpe 추적
  - MDD >= 10% WARNING, >= 15% CRITICAL -- CircuitBreaker 트리거
  - 세션 요약에 전략별 Rolling 성과 출력
- `tests/test_bundle_oos.py` -- 11개 테스트 ALL PASS (기존 88개 영향 없음, 전체 99개 PASS)

---

### ✅ Cycle 178 완료 사항 (A+B+C)

#### A(전략): Rolling OOS Validator ✅ COMPLETE
- `RollingOOSValidator` in `src/backtest/walk_forward.py`
- 6m IS / 2m OOS Rolling, WFE ≥ 0.50, Sharpe decay ≤ 40%, MDD expand ≤ 2x
- **다음**: 실제 Bybit 데이터로 5-bundle 전략 OOS 실행

#### B(리스크): Strategy Correlation + Risk Parity ✅ COMPLETE
- `StrategyCorrelationAnalyzer` in `src/risk/portfolio_optimizer.py`
- 상관행렬 + inv-vol 가중치 + 높은 상관 쌍 자동 감지
- **다음**: 실제 5-bundle 거래 데이터로 상관행렬 계산 + cmf-elder_impulse 확인

#### C(데이터): Performance Monitor + Telegram ✅ COMPLETE
- `PerformanceMonitor` + rolling PF/MDD in `src/risk/performance_tracker.py`
- MDD ≥ 10% WARNING, ≥ 15% CRITICAL 알림, 레짐 전환 알림
- **다음**: paper_trader.py에 PerformanceMonitor 연결

### 🎯 Cycle 180 권장 작업 (180 mod 5 = 0 → A+B+C)

#### A(전략): RegimeDetector → paper_trader 실제 연결
- `src/exchange/paper_trader.py` 에 RegimeDetector + RegimeStrategyRouter 통합
- PerformanceMonitor.regime_change_alert() 호출 연결
- 2봉 연속 확인 후 전략 스위칭 로직 구현

#### B(리스크): 5-Bundle 실데이터 OOS 실행
- Bybit BTCUSDT 4h봉 데이터로 RollingOOSValidator 실행
- 5전략 WFE, Sharpe decay, MDD expand 실측

#### C(데이터): Paper Trading 4주 자동화 스크립트
- 주간 WFE 체크 자동 스크립트 (cron 기반)
- Go/No-Go 판정 자동화: PF ≥ 1.4, MDD ≤ 15%, WFE ≥ 0.50
- 5% 급락 구간 포함 여부 자동 체크

---

### ⚠️ 핵심 문제 및 해결책

**문제:** 실데이터 성능 > 합성데이터 성능 역전 (Sharpe -2.84)
- PASS 기준: Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%
- 현재 15개 전략 모두 기준 충족 (합성은 22개 PASS)

**해결책:**
1. **Regime filtering:** 레짐별 로테이션으로 거래 빈도 4-5x 증가 (15 → 60-75 거래/월)
2. **Position sizing:** Crisis mode 50% reduction으로 tail risk 제거
3. **Live validation:** 레짐별 PF 추적 (목표: 각 레짐 PF > 1.4)
4. **WFE 기준 추가:** OOS_Sharpe / IS_Sharpe ≥ 0.50 (engine.py에 MIN_WFE=0.5 이미 구현)

---

### 📋 OOS 검증 방법론 (Cycle 177 F 리서치 결과)

#### Walk-Forward 권장 설정 (크립토 특화)
- **비율:** IS 70% / OOS 30% (표준); 크립토 구조 변화 빠름 → Rolling 방식
- **Fold 단위:** IS 6개월 / OOS 2개월 (3:1), 다음 fold는 2개월씩 슬라이드
- **WFE 기준:** OOS_ann_profit / IS_ann_profit ≥ 0.50 → PASS
- **Overfitting 탐지:** OOS Sharpe < IS Sharpe × 0.60 OR OOS MDD > IS MDD × 2.0 → FAIL

#### CPCV 적용 범위
- cmf, elder_impulse (파라미터 민감): CPCV 5-fold + 1봉 embargo → DSR 계산
- wick_reversal, narrow_range, value_area (rule-based): Walk-Forward만으로 충분

---

### 📋 Paper Trading 자동화 판정 기준 (Cycle 179 F 리서치 결과)

| 지표 | Go 조건 | No-Go 트리거 |
|------|---------|-------------|
| Profit Factor | ≥ 1.4 | < 1.0 즉시 중단 |
| MDD | ≤ 15% | > 20% 즉시 중단 |
| Sharpe (rolling 4주) | ≥ 0.8 | < 0.3 |
| WFE (OOS/IS 수익 비율) | ≥ 0.50 | < 0.30 |
| 주간 승률 | ≥ 45% | < 30% |
| API 에러율 | 0% | ≥ 3% 중단 |
| PSI 드리프트 | < 0.1 | > 0.2 신호 중단 |

스케줄러: VPS → systemd (`Restart=always`), Docker → Ofelia
API 복구: 지수 백오프(1/2/4/8/16초) + Circuit Breaker(3회 실패→disabled) + 포지션 동기화

---

### 📋 5-Strategy Bundle 상관관계 + 가중치 (Cycle 177 F 리서치 결과)

#### 상관관계 관리
- 목표: 페어 평균 |r| < 0.30
- cmf + elder_impulse 예상 상관: 0.60-0.70 (둘 다 TREND momentum) → 주의
- 완화: TREND 레짐에서 cmf 단독 (Sharpe 6.85 우선), elder_impulse 대기
- 반대신호(BUY vs SELL) 동시 발생 시 → flat 유지 (양쪽 무시)

#### 가중치 방법
- Risk Parity(1/σ) 권장: 크립토 CVaR 연구에서 하락장 MDD 30% 감소 확인
- 공식: `w_i = (1/σ_i) / sum(1/σ_j)`, σ = 최근 20거래 수익률 표준편차, 매주 재계산
- Crisis 레짐 시: 가중치 무관, 전체 포지션 0.5x 적용

---

### 📊 Strategy Performance Reference (Real Data)

| Strategy | Sharpe | Win% | PF | Trades | MDD | Regime |
|----------|--------|------|-------|--------|-----|--------|
| cmf | 6.85 | 57% | 2.29 | 28 | 4.3% | TREND |
| wick_reversal | 6.51 | 54% | 2.03 | 35 | 3.5% | RANGE |
| volume_breakout | 5.91 | 60% | 2.66 | 15 | 2.2% | TREND |
| elder_impulse | 6.29 | 63% | 2.70 | 16 | 3.5% | TREND |
| momentum_quality | 5.54 | 52% | 1.92 | 27 | 3.2% | TREND |
| engulfing_zone | 5.50 | 60% | 2.50 | 15 | 3.3% | RANGE |
| supertrend_multi | 5.38 | 48% | 1.97 | 25 | 4.4% | TREND |
| value_area | 5.24 | 53% | 1.84 | 30 | 5.0% | RANGE |
| price_action_momentum | 5.24 | 59% | 2.24 | 17 | 2.2% | TREND |
| frama | 4.37 | 51% | 1.62 | 35 | 4.6% | RANGE |
| price_cluster | 4.51 | 53% | 2.06 | 15 | 2.2% | RANGE |
| narrow_range | 4.31 | 50% | 1.61 | 34 | 4.3% | RANGE |
| htf_ema | 4.91 | 52% | 1.85 | 25 | 3.2% | TREND |
| relative_volume | 3.76 | 50% | 1.76 | 18 | 3.3% | TREND |
| acceleration_band | 3.45 | 48% | 1.51 | 27 | 5.2% | TREND |
| positional_scaling | 3.72 | 50% | 1.74 | 18 | 3.3% | RANGE |
| order_flow_imbalance_v2 | 5.00 | 52% | 1.77 | 31 | 4.3% | RANGE |
| dema_cross | 3.81 | 50% | 1.70 | 20 | 3.2% | TREND |
| linear_channel_rev | 4.62 | 50% | 1.85 | 24 | 5.3% | RANGE |
| roc_ma_cross | 2.98 | 50% | 1.58 | 18 | 2.5% | TREND |

**평균:** Sharpe 5.04, PF 1.98, Win% 53%, MDD 3.7%

---

### 🚀 라이브 배포 체크리스트 (Cycle 179 F 업데이트)

**5-Strategy Bundle:** cmf (TREND, 6.85) / elder_impulse (TREND, 6.29) / wick_reversal (RANGE, 6.51) / narrow_range (RANGE/BO, 4.31) / value_area (RANGE, 5.24)

#### Phase 1: OOS 검증 (Cycle 178 A)
- [ ] Walk-Forward: IS 70%/OOS 30%, Rolling 6m/2m fold 실행
- [ ] WFE ≥ 0.50 for all 5 strategies
- [ ] OOS Sharpe ≥ IS Sharpe × 0.60
- [ ] OOS MDD ≤ IS MDD × 2.0
- [ ] Monte Carlo p-value < 0.05 for all 5
- [ ] CPCV DSR for cmf, elder_impulse

#### Phase 2: 포트폴리오 검증 (Cycle 178 B)
- [ ] 5-strategy 일일 수익률 상관행렬 (목표: |r| < 0.30)
- [ ] cmf-elder_impulse 상관 > 0.50 시 → TREND 레짐 cmf 단독 전환
- [ ] Risk Parity 가중치 계산 및 적용

#### Phase 3: 모니터링 인프라 (Cycle 178 C)
- [ ] Rolling 4주 Sharpe/PF 실시간 추적 (4h 업데이트)
- [ ] MDD > 10% → Telegram 경고
- [ ] MDD > 15% → 자동 포지션 청산 + 중단 (circuit breaker)
- [ ] API 장애: 지수 백오프(1/2/4/8/16초) → Circuit Breaker(3회→disabled) → 포지션 동기화

#### Phase 4: Paper Trading (4주 자동화)
- [ ] Regime switching 통합 완료 (D+E Cycle 179 대기 중)
- [ ] 레짐별 > 15거래 확인
- [ ] 4주 paper trading 자동 실행 (5% 급락 구간 포함 필수)
- [ ] 주간 WFE 자동 체크 (cron 또는 systemd timer)
- [ ] Go/No-Go 자동 판정: PF ≥ 1.4, MDD ≤ 15%, WFE ≥ 0.50

#### Go/No-Go 기준
| 지표 | 기준 |
|------|------|
| Paper PF (4주) | ≥ 1.4 |
| Paper MDD (4주) | ≤ 15% |
| WFE | ≥ 0.50 |
| OOS Sharpe | ≥ 3.0 (IS 5.5 기준 60%) |
| Regime 정확도 | ≥ 80% |
| API 장애 복구 | ≤ 30초 |
| 5% 급락 구간 포함 | 최소 1회 |

---

**상태**: Cycle 179 D+E+F 완료 → Cycle 180 A(실데이터 OOS 실행) + B(RegimeDetector 통합) + C(paper 자동화)
**다음 담당자 접수 사항**: `python3 scripts/run_bundle_oos.py` 실행 + RegimeDetector→paper_trader 연결 + 4주 자동 paper trading 스크립트
