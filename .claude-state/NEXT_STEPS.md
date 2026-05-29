# Next Steps

_Last updated: 2026-05-29 (Cycle 244 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 240, 241, 242, 243, 244

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 240 | D+E+SIM+F | regime별 importance, feature drift, check_strategy_health |
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |

### 🎯 Cycle 245 작업 방향 (245 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): value_area 4h 타임프레임 대응 검토
- Cycle 244 Bundle OOS: value_area 모든 fold 0 trades (4h 봉에서 신호 미생성)
- `BUNDLE_STRATEGIES`에서 value_area 타임프레임 관련 파라미터 조정 또는 검증 기준 완화
  - va_period 15→10으로 축소하여 신호 빈도 증가 시도
  - 또는 4h 대신 1h 전용 테스트 스크립트 추가 고려
- 기존 테스트 커버리지 확인: `test_bundle_oos.py` value_area 관련 테스트 추가

#### A(품질): Paper SIM 상위 전략 안정성 개선
- relative_volume (SharpeStd=0.51, 가장 안정적, MDD=9.3%) → 일관성 필터 분석
  - 4개 윈도우 중 어느 윈도우가 FAIL인지 확인
  - Sharpe std 낮은 이유 분석 → 다른 전략에 적용 가능한 로직 도출
- volatility_cluster (SharpeStd=0.40, 최저) — 안정성 유지 요인 확인

#### C(데이터): 합성 데이터 품질 개선
- 현재 GBM BlockBootstrap 데이터: IS Sharpe 100% 음수 전략 다수
- 더 현실적인 가격 시뮬레이션 고려: regime-switching 모델 추가
  - HMM 기반 Bull/Bear 레짐 전환 포함한 합성 데이터 생성
  - `heston_model.py` 활용 확대 (현재 미활용)

#### F(리서치): WFE sign reversal fix 효과 측정
- Cycle 244에서 IS < -1.0 + OOS > 0 → WFE=0.0 fix 적용
- 이 변경이 전체 PASS 기준 강화에 미치는 효과:
  - elder_impulse: 이전 PASS fold 1개 → 0개 (OOS Sharpe std=4.691 → 전략 평가 미변화)
  - wick_reversal: avg_wfe 0.222 → 0.000 (더 엄격한 평가)
- 실거래소 데이터에서 동일 패턴 검증 필요 (SSL 차단으로 현재 불가)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭
- Paper SIM 상위: volume_breakout(composite 75.7), order_flow_imbalance_v2(74.7), price_action_momentum(74.5)
- 가장 안정적: volatility_cluster(SharpeStd=0.40), relative_volume(SharpeStd=0.51)
- 테스트: 175 passed, 3 skipped (Cycle 244 변경 기존 테스트 모두 통과)
- WFE 역방향 fix: IS < -1.0 + OOS > 0 → WFE = 0.0 (engine.py + walk_forward.py)
- avg_slippage_per_trade: BacktestResult에 신규 추가
- compute_ensemble_weight_recency: fold_sharpes + sign_reversal_penalty 파라미터 추가
