# Next Steps

_Last updated: 2026-05-27 (Cycle 226 코드 완료 + Bundle OOS 결과)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 로테이션: Cycle 226 코드 완료
- 226 mod 5 = 1 → **B(리스크) + D(ML) + F(리서치)**
- B(리스크) 2개 작업 완료:
  1. kelly_sizer.py: Cornish-Fisher CF 클리핑 (극단 skew/kurtosis 방어)
  2. kelly_sizer.py: compute_from_trades() + Bayesian shrinkage 추가
- D(ML) 1개 작업 완료:
  1. trainer.py: StandardScaler use_scaler=False 옵션 추가 (look-ahead 방지)
- Bundle OOS: 0/5 PASS (OOS Sharpe std 3.4~6.4 불안정)
- Paper Simulation: 실행 중 (SSL 제약 합성 데이터)

### Cycle 226 SIM 결과 (BTC/USDT, 합성 BlockBootstrap)

#### Paper Simulation (1h, 3심볼)
- **0/22 PASS** — 전 전략 mc_p_value > 0.05 주요 원인
- BTC 평균 수익률: +30.98%, Top: price_action_momentum (+120.35%)
- 상위 전략은 Sharpe>1.0, PF>1.5, MDD<20% 모두 충족 — mc_p_value만 탈락
- **핵심 발견**: 합성 BlockBootstrap 데이터에서 mc_p_value 편향 확인
  - mc_p_threshold 0.05 → 0.10 완화 검토 필요 (실전 데이터 검증 후)

#### BTC 상위 3 전략 (실전 검증 최우선 후보)
| 전략 | Sharpe | PF | Trades | MDD | SharpeStd |
|-----|--------|-----|--------|-----|-----------|
| supertrend_multi | 7.39 | 2.25 | 118 | 6.8% | 1.31 |
| momentum_quality | 6.25 | 1.93 | 123 | 8.1% | 1.07 |
| price_action_momentum | 6.58 | 1.79 | 166 | 13.6% | 1.21 |

#### Bundle OOS (4h, BTC/USDT)
- **0/5 PASS** — cmf, elder_impulse, wick_reversal, narrow_range, value_area
- OOS Sharpe std 전부 >1.5 (3.4~6.4) — 파라미터 불안정

### 🎯 Cycle 227 작업 방향 (227 mod 5 = 2 → B(리스크) + D(ML) + F)

#### B(리스크): mc_p_value 임계값 완화 검토
- `scripts/paper_simulation.py`의 MC permutation test 임계값 0.05 → 0.10 옵션 추가
  - 합성 데이터에서 p_threshold=0.10으로 재실행 시 PASS 전략 증가 예측
  - 실전 데이터 사용 가능 시 p_threshold=0.05 유지

#### D(ML): use_scaler=True 기본화 실험
- WalkForwardTrainer(use_scaler=True) 로 재학습 → test_accuracy 변화 관찰
- StandardScaler가 feature importance에 미치는 영향 분석

#### F(리서치): 상위 전략 강건성 분석
- supertrend_multi, momentum_quality, price_action_momentum 실전 데이터 검증 최우선
- SharpeStd가 낮은 order_flow_imbalance_v2(std=0.30) 안정성 주목

---

### Cycle 225 SIM 결과 (BTC/USDT, 합성 BlockBootstrap)

#### value_area va_mult=0.6 효과
- **이전 (va_mult=0.7)**: avg_trades=16
- **현재 (va_mult=0.6)**: avg_trades=18.2 (+14%)
  - Window별: 8, 18, 25, 22 (Window 2-4는 trades>=15 충족)
- **성과는 부진**: avg_sharpe=-2.73, avg_pf=0.54, avg_return=-7.6%
  - trades 수는 증가했지만 전략 자체가 합성 데이터에서 손실
  - 모든 윈도우에서 sharpe < 0, pf < 1.0

#### 전체 결과 요약
- **22전략 전부 FAIL** (0/22 PASS, consistency 0/4)
- 평균 수익률: +13.44%, 최고: price_action_momentum (+68.5%)

#### 상위 5 전략 (Composite Rank Score)
| Rank | Strategy | Score | Sharpe | PF | Trades | MDD |
|------|----------|-------|--------|-----|--------|-----|
| 1 | volatility_cluster | 76.1 | 3.82 | 1.77 | 63 | 6.4% |
| 2 | price_action_momentum | 73.3 | 4.20 | 1.49 | 156 | 15.5% |
| 3 | momentum_quality | 69.4 | 3.25 | 1.45 | 103 | 10.7% |
| 4 | roc_ma_cross | 64.4 | 2.01 | 1.58 | 34 | 6.0% |
| 5 | supertrend_multi | 63.1 | 2.49 | 1.38 | 84 | 10.5% |

#### FAIL 원인 카테고리별 빈도 (전체 202건)
| 원인 | 건수 | 비율 |
|------|------|------|
| mc_p_value > 0.05 | 80 | 39.6% |
| profit_factor < 1.5 | 65 | 32.2% |
| sharpe < 1.0 | 41 | 20.3% |
| max_drawdown > 20% | 8 | 4.0% |
| trades < 15 | 8 | 4.0% |

- **mc_p_value가 1위 (39.6%)** — 합성 데이터에서 신호 통계적 유의성 부족
- **profit_factor 2위 (32.2%)** — 대부분 PF 1.2~1.5 구간에서 마진 탈락

### Cycle 226 D(ML) 완료
- **WalkForwardTrainer `use_scaler`** 추가: `src/ml/trainer.py`
  - train set으로 StandardScaler fit, val/cal/test에 transform만 적용
  - `save()`의 pkl payload에 `scaler` 키 포함
  - 기존 기본값 `use_scaler=False`로 하위 호환 유지
- **drift_detector.py ADWIN 파라미터**: 변경 불필요
  - `delta=0.05` (금융 시계열 표준), `min_window=32` (>= 30) — 이미 적절
- 테스트: `test_adwin_drift.py` 41 passed, `test_trainer.py` 53 passed, 3 skipped

### 🎯 Cycle 227 작업 방향

#### A(품질): 아직 남은 항목
- quality_audit 재실행하여 value_area PASS 여부 확인
- MLSignalGenerator regime_aware 추론 통합 테스트 추가

#### F(리서치): 실전 데이터 전략 방향성
- **크로스 심볼 공통 상위 3**: `momentum_quality`, `price_action_momentum`, `supertrend_multi`
  → 실거래소 데이터 검증 최우선 후보
- `volatility_cluster`: BTC에서 Rank 1위 (score 76.1, MDD 6.4%) → 안정성 우수
- `roc_ma_cross`: PF 1.58로 유일하게 PF 기준 근접 충족

#### mc_p_value FAIL 대응 방향
- 합성 데이터 한계: MC test가 합성 데이터의 랜덤 특성에 민감
- 실제 거래소 데이터에서 재검증이 최우선 (SSL 환경 해제 후)
- mc_p_threshold 완화(0.05→0.10) 검토 가능하나, 실전 데이터 확인 전까지 보류

### ⚠️ 원격 환경 제약
- SSL 인터셉션으로 외부 거래소 API 전면 차단
- 합성 데이터 결과는 방향성 참고만 — "실전 PASS"라 단정 금지

### Cycle 226 B(리스크) 완료
- **kelly_sizer.py** CF-VaR 극단값 클리핑 추가:
  -  clipped to [-5, 5],  to [-2, 50] (z_cf 발산 방지)
- **kelly_sizer.py**  메서드 추가:
  - 빈 리스트, 모두손실, 모두수익, NaN/inf, 소표본 Bayesian shrinkage 모두 처리
  - _trade_history deque에 자동 기록
- 테스트: 70 passed (test_kelly_sizer_regime_edge_cases, test_kelly_integration, test_kelly_cornish_fisher)

**상태**: Cycle 226 B(리스크) 완료
**최우선 과제**: 실거래소 데이터 접근 시 상위 전략 재검증
