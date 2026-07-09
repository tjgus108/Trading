# Current Cycle Briefing

_Last updated: 2026-07-09 (Cycle 407 완료)_

## 현재 상태

- **완료된 사이클**: 407
- **다음 사이클**: 408 (408 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정 (음의 엣지, 탐색 금지)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정, 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8642 총계 (8619 passed + 23 skipped) — Cycle407 +8 추가

## Cycle 407 주요 결과

### B(리스크): CircuitBreaker 복합 케이스 테스트 (3개 추가)

- `tests/test_circuit_breaker.py`:
  - `test_daily_drawdown_exact_boundary_with_atr_surge`: daily_dd==limit 경계값 + ATR surge → 낙폭 우선
  - `test_rapid_decline_does_not_set_is_triggered`: rapid_decline → result["triggered"]=True이지만 cb.is_triggered=False (비영속적 트리거 동작 명시)
  - `test_consecutive_loss_cooldown_ignores_atr_surge`: 쿨다운 + ATR surge → 쿨다운 우선

### D(ML): optimize_frama() 타입 + optimize_narrow_range() 엣지케이스 (5개 추가)

- `tests/test_phase_d.py` (TestOptimizeFrama):
  - `test_optimize_frama_avg_oos_sharpe_is_float`: avg_oos_sharpe isinstance float 검증
  - `test_optimize_frama_oos_sharpe_std_non_negative`: oos_sharpe_std >= 0.0
- `tests/test_phase_d.py` (TestOptimizeNarrowRange, 신규):
  - `test_optimize_narrow_range_single_window_no_crash`: n_windows=1 크래시 없음
  - `test_optimize_narrow_range_result_fields_present`: 핵심 필드 avg_oos_sharpe/best_params/oos_sharpe_std 존재
  - `test_optimize_narrow_range_oos_sharpe_std_non_negative`: oos_sharpe_std >= 0.0

### F(리서치): acceleration_band 1h BTC 구조적 실패 확정

- BTC 1h: Sh=-0.94, **PF=0.98(<1.0=음의 엣지)**, Trades=44, Consistency=1/8
- ETH 1h: Sh=-2.03, Trades=13(<15) — 신호 부족; SOL 1h: Sh=-0.80, Trades=11(<15) — 신호 부족
- 근본 원인: ATR band breakout 전략은 TRENDING 환경 적합, BTC 1h 47.3% RANGING → 허위 돌파 과다
- 파라미터화 가능 요소 없음 (period=20, margins 하드코딩)
- 결론: acceleration_band 추가 탐색 금지 → `src/backtest/walk_forward.py` DEFAULT_GRIDS["acceleration_band"]={} + 주석 추가

## 다음 사이클 (408): C+D+F (408 mod 5 = 3 → C+B+F)

- **C(데이터)**: DataFeed 지표 엣지케이스 또는 WebSocketDataAdapter 미커버 케이스
- **B(리스크)**: DrawdownMonitor 또는 KellySizer 미커버 케이스
- **F(리서치)**: htf_ema (rank 13, BTC 1h Sh=-0.72, Tr=43) 구조 분석 또는 positional_scaling 보류 유지 검토
