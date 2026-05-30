# Next Steps

_Last updated: 2026-05-30 (Cycle 246 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~246

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(DrawdownMonitor), mc_min_trades/mc_block_size(BacktestEngine), 5 신규 테스트 |

### 🎯 Cycle 247 작업 방향 (247 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): KellySizer와 DrawdownMonitor 연동 실제 호출 경로 검증
- Cycle 246에서 DrawdownMonitor.get_kelly_fraction_multiplier() 추가 완료
- 다음: `src/risk/manager.py` 또는 포지션 사이저에서 이 값을 실제로 KellySizer.compute()에 전달하는지 확인
- `kelly_fraction_multiplier` 신호를 portfolio-level allocation에 연결 (risk/manager.py)
- lob_maker AvgMDD=20.0%, cmf AvgMDD=21.1% → 8% MDD 조기 감지 후 Kelly 0.5x 축소 효과 시뮬레이션

#### D(ML): mc_min_trades 활용 + block permutation test 효과 분석
- Cycle 246: mc_min_trades, mc_block_size 파라미터 노출 완료
- 다음: mc_min_trades=20 설정 시 price_action_momentum(146 trades) p-value 변화 분석
- mc_block_size=24 (1h → daily blocks) 적용 시 serial correlation 보존 효과 확인
- paper_simulation.py에서 --mc-block-size, --mc-min-trades 인수 추가 고려

#### F(리서치): value_area min_oos_trades 완화 검토
- Bundle OOS 4h: value_area max 8 trades/fold (min_oos_trades=10 기준 미달)
- 옵션 1: min_oos_trades 10→5 완화 (`run_bundle_oos.py --min-trades 5`)
- 옵션 2: _VA_MULT 추가 완화 (0.6→0.5) 후 Bundle OOS 재실행
- 실거래소 데이터 접근 시 1h value_area 우선 검증

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭 (Cycle 246 이후)
- Paper SIM 상위 BTC: price_action_momentum(Sharpe 5.42), momentum_quality(3.31), supertrend_multi(2.80)
- mc_p_value 패턴: 0.124~0.494 (합성 데이터 한계로 p < 0.05 달성 불가)
- value_area: Bundle OOS fold 6 PASS (Sharpe 1.775), min_oos_trades=10 장벽
- 테스트: **8332 passed** (Cycle 246 신규 5개 kelly_reduce_at_mdd 포함)
- 신규 API: DrawdownMonitor.get_kelly_fraction_multiplier(), BacktestEngine(mc_min_trades, mc_block_size)
