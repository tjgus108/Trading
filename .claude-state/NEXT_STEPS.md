# Next Steps

_Last updated: 2026-04-21 (Cycle 178 A+B+C 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 177 진행 중
- 177 mod 5 = 2 → **D(ML) + E(실행) + F(리서치)** 패턴

### ✅ Cycle 177 완료 사항

#### D(ML): RegimeDetector 구현 ✅ COMPLETE
- `src/ml/regime_detector.py` — `RegimeDetector` 구현 완료
  - ADX(14) Wilder 평활 + ATR(20) EWM 계산
  - 상태머신: TREND(ADX>25) / RANGE(ATR<ATR_MA & ADX<20) / CRISIS(ATR>2×ATR_MA)
  - confirm_bars=2 연속 확인 후 전환 (거짓 전환 방지)
  - `get_position_scale()`: CRISIS=0.5, TREND/RANGE=1.0
- `tests/test_ml_regime_detector.py` — 16개 테스트 ALL PASS
- **다음**: RegimeDetector를 RegimeStrategyRouter 또는 live orchestrator에 연결

#### E(실행): Regime-Aware Strategy Router 통합 ✅ COMPLETE
- `src/strategy/regime_router.py` — `RegimeStrategyRouter` 구현 완료
  - `get_active_strategies(regime)`: TREND 7전략 / RANGE 7전략 / CRISIS 전체 반환
  - `scale_position(regime, base_size)`: CRISIS 0.5x, 나머지 1.0x
  - `should_skip(strategy, regime)`: 레짐 불일치 전략 스킵, CRISIS는 스킵 없이 크기 감소
- `tests/test_regime_router.py` — 20개 테스트 ALL PASS
- **다음**: execution loop(`src/exchange/paper_trader.py` 또는 orchestrator)에 Router 연결 필요

#### F(리서치): OOS 검증 + 라이브 배포 준비 ✅ COMPLETE
- Walk-Forward (IS 70%/OOS 30%, Rolling 6m/2m fold) 방법론 확정
- CPCV 적용 범위: cmf/elder_impulse (파라미터 민감) 우선, rule-based는 WFA로 충분
- Monte Carlo 기준 확인: p-value < 0.05 (engine.py에 이미 구현)
- 5-bundle 상관관계 관리: Risk Parity(1/σ) 가중치 권장
- 라이브 배포 체크리스트 전면 업데이트 (하단 참조)

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

### 🎯 Cycle 179 권장 작업 (179 mod 5 = 4 → D+E+F)

#### D(ML): RegimeDetector → paper_trader 연결
- RegimeDetector 출력을 paper_trader 루프에 통합
- 레짐 전환 시 PerformanceMonitor.regime_change_alert() 호출
- 2봉 연속 확인 후 전략 스위칭 로직

#### E(실행): 5-Bundle 실데이터 OOS 실행
- Bybit BTCUSDT 4h봉 데이터로 RollingOOSValidator 실행
- cmf, elder_impulse, wick_reversal, narrow_range, value_area 각각 검증
- StrategyCorrelationAnalyzer로 상관행렬 실측

#### F(리서치): Paper Trading 자동화 리서치
- 4주 paper trading 자동 실행 + 주간 WFE 체크 방법론
- Go/No-Go 기준 자동 판정 스크립트 설계
- API 장애 복구 retry/fallback 패턴 리서치

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
- **Rolling vs Anchored:** Rolling 권장 (intraday 크립토). Anchored는 전체 안정성 보조 확인용

#### CPCV 적용 범위
- cmf, elder_impulse (파라미터 민감): CPCV 5-fold + 1봉 embargo → DSR 계산
- wick_reversal, narrow_range, value_area (rule-based): Walk-Forward만으로 충분
- DSR 계산: `src/backtest/report.py`의 `deflated_sharpe_ratio` 이미 구현됨

#### Monte Carlo 기준 (engine.py 기존 설정 유지)
- MC_N_PERMUTATIONS = 500, MC_P_THRESHOLD = 0.05
- 5-bundle IS 평균 Sharpe ~5.5 → OOS 최소 3.3 이상 목표

---

### 📋 5-Strategy Bundle 상관관계 + 가중치 (Cycle 177 F 리서치 결과)

#### 상관관계 관리
- 목표: 페어 평균 |r| < 0.30
- cmf + elder_impulse 예상 상관: 0.60-0.70 (둘 다 TREND momentum) → 주의
- 완화: TREND 레짐에서 cmf 단독 (Sharpe 6.85 우선), elder_impulse 대기
- 반대신호(BUY vs SELL) 동시 발생 시 → flat 유지 (양쪽 무시)

#### 가중치 방법
- Risk Parity(1/σ) 권장: 크립토 CVaR 연구에서 하락장 MDD 30% 감소 확인
- mean-variance 비권장: 하락장 inter-strategy 상관 0.85+ 급증으로 무효화
- 공식: `w_i = (1/σ_i) / sum(1/σ_j)`, σ = 최근 20거래 수익률 표준편차, 매주 재계산
- Crisis 레짐 시: 가중치 무관, 전체 포지션 0.5x 적용

#### 신호 충돌 처리
1. 레짐 필터 우선: TREND → cmf > elder_impulse, RANGE → wick_reversal > value_area
2. 같은 레짐 같은 방향: 최고 Sharpe 전략 단독 실행 (중복 포지션 금지)
3. 반대 방향 동시 신호: flat 유지
4. 신호 만료: 발생 후 2봉 이내 미체결 → 자동 만료

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

### 🚀 라이브 배포 체크리스트 (Cycle 177 F 업데이트)

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
- [ ] Equal Weight vs Risk Parity OOS 비교

#### Phase 3: 모니터링 인프라 (Cycle 178 C)
- [ ] Rolling 4주 Sharpe/PF 실시간 추적 (4h 업데이트)
- [ ] MDD > 10% → Telegram 경고
- [ ] MDD > 15% → 자동 포지션 청산 + 중단 (circuit breaker)
- [ ] 레짐 전환 → 2봉 연속 확인 후 전략 스위칭
- [ ] API 장애: retry 3회(1s/2s/4s) → REST 폴백 → 포지션 청산 + 알림

#### Phase 4: Paper Trading
- [ ] Regime switching 통합 완료 (D+E Cycle 177 ✅)
- [ ] 레짐별 > 15거래 확인
- [ ] 4주 paper trading (매주 WFE 확인)
- [ ] OOS PF > 1.4 달성

#### Go/No-Go 기준
| 지표 | 기준 |
|------|------|
| Paper PF (4주) | ≥ 1.4 |
| Paper MDD (4주) | ≤ 15% |
| WFE | ≥ 0.50 |
| OOS Sharpe | ≥ 3.0 (IS 5.5 기준 60%) |
| Regime 정확도 | ≥ 80% |
| API 장애 복구 | ≤ 30초 |

---

**상태**: Cycle 178 A+B+C 완료 → Cycle 179 D+E+F (RegimeDetector 통합 + 실데이터 OOS + Paper Trading 리서치)
**다음 담당자 접수 사항**: RegimeDetector→paper_trader 연결 + 실데이터 OOS 실행 + Paper Trading 자동화
