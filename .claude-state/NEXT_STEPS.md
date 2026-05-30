# Next Steps

_Last updated: 2026-05-30 (Cycle 248 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~248

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(DrawdownMonitor), mc_min_trades/mc_block_size(BacktestEngine), 5 신규 테스트 |
| 247 | B+D+SIM+F | kelly_fraction_multiplier→manager.py 연결, paper_sim --mc-min-trades/--mc-block-size, 2 신규 테스트 |
| 248 | C+B+SIM+F | generate_synthetic_data() regime 파라미터 개선, regime=None MDD=9% 복합 테스트, --min-trades 5 검증 |

### 🎯 Cycle 249 작업 방향 (249 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): IS Sharpe 음수 전략을 위한 대안 합성 데이터 탐색
- Cycle 248 결론: P(bull→bear) 조정만으로는 IS Sharpe 음수 해소 불가 (전략 신호가 GBM과 근본 충돌)
- 옵션: `quality_audit.make_synthetic_data()` (BlockBootstrap 기반)로 Bundle OOS 합성 데이터 교체 검토
- `run_bundle_oos.py`의 `generate_synthetic_data()` → `quality_audit.make_synthetic_data()` fallback 시 비교
- elder_impulse 전략 신호 구조 분석: IS 음수 원인이 entry/exit 로직 또는 피처 계산 오류인지 확인

#### E(실행): Paper Trading slippage 모델 검증
- `avg_slippage_per_trade` (Cycle 244 추가): 실제 활용되는지 확인
- `TwapExecutor` 또는 `VwapExecutor` 테스트 coverage 확인
- 슬리피지 0.05%가 합성 시뮬에서 P&L에 미치는 영향 정량화

#### F(리서치): cmf 전략 우위 분석 (Bundle OOS Rank #1 유지)
- cmf가 합성 데이터에서도 상대적으로 우세한 이유 분석 (OOS Sharpe -1.473 → 가장 덜 나쁨)
- cmf vs value_area 신호 생성 메커니즘 비교: cmf는 volume-based → GBM 거래량 모델과 상성
- 실거래소 데이터 접근 시 cmf 4h 우선 검증

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터 fallback 불가피)
- IS Sharpe 음수 근본 원인: 합성 GBM 데이터 자체가 trend-following 전략과 충돌 (해결 미완료)
- Paper SIM: `--mc-min-trades 20` 재실행 필요 (Cycle 248에서 타임아웃으로 미완료)

### 핵심 메트릭 (Cycle 248 이후)
- Bundle OOS Rank #1: cmf (Score 79.9, OOS Sharpe -1.473, Avg Trades 12.4, OOS MDD 7.64%)
- generate_synthetic_data() regime: P(bull→bear) 0.01, P(bear→bull) 0.04, drift ±0.03%
- value_area --min-trades 5: 0/PASS (56% fold 저거래, 실거래소 데이터 없이 검증 불가)
- kelly_fraction_multiplier 복합: regime=None + MDD=9% → 0.25x (test_regime_none_mdd9_compound 추가)
- 테스트: **8340 passed** (Cycle 248 신규 1개 test_regime_none_mdd9_compound)
