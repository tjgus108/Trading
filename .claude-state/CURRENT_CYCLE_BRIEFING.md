# Current Cycle Briefing

_Last updated: 2026-07-08 (Cycle 407 완료)_

## 현재 상태

- **완료된 사이클**: 407
- **다음 사이클**: 408 (408 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **acceleration_band**: Sh=-0.94, PF=0.98, Tr=44, 1/8 → 구조적 한계 확정 (OR조건 과완화, 1h breakout 노이즈), 탐색 보류
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정 (Cycle406), 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (Cycle405), 탐색 보류
- **Bundle OOS**: 5/5 PASS (SSL fallback으로 갱신 불가, 보존)
- **전체 테스트 수**: 8641 총계 (8618 passed + 23 skipped) — Cycle407 +7 추가

## Cycle 407 주요 결과

### B(리스크): CircuitBreaker 복합 케이스 테스트 (3개 추가)

- `tests/test_circuit_breaker.py`:
  - `test_reset_daily_does_not_clear_consecutive_loss_cooldown`: reset_daily() → 일일 상태만, 쿨다운 유지
  - `test_daily_drawdown_and_rapid_decline_drawdown_wins`: daily_dd 우선순위2 > rapid_decline 우선순위4
  - `test_max_daily_trades_and_atr_surge_trades_limit_wins`: max_daily_trades 우선순위5 > ATR surge 우선순위6

### D(ML): optimize_frama() 타입 검증 + TestOptimizeNarrowRange 신규 (4개 추가)

- `tests/test_phase_d.py`:
  - `test_optimize_frama_avg_oos_sharpe_is_float`: avg_oos_sharpe float 타입
  - `test_optimize_frama_oos_sharpe_std_non_negative`: oos_sharpe_std >= 0
  - `test_optimize_narrow_range_single_window_no_crash` (TestOptimizeNarrowRange 신규): n_windows=1
  - `test_optimize_narrow_range_result_fields_present`: 핵심 필드 검증

### F(리서치): acceleration_band 1h BTC 구조적 한계 분석 완료

- **BTC 1h**: Sh=-0.94, PF=0.98(<1.0!), Trades=44, 1/8 Consistency (rank15)
- 근본 원인: OR 조건(`trend_up OR vol_ok`) 과완화 → vol_ok는 대부분 캔들 True → 거짓 돌파
- strong_band(band_width>0.025)가 신호 게이팅 없음 (confidence만 결정)
- 1h BTC breakout 계열 구조적 한계 계보: narrow_range(406) → engulfing_zone(404) → acceleration_band(407)
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["acceleration_band"] 구조적 한계 주석 추가

## 다음 사이클 (408): C+B+F

- **C(데이터)**: DataFeed return_5/ema20_slope/volume=0 엣지케이스 (test_feed_boundary.py)
- **B(리스크)**: DrawdownMonitor set_ranging_macro_neutral + from_dict legacy state 엣지케이스
- **F(리서치)**: dema_cross PF=1.38 → 1.50 갭 마지막 분석 (rsi_dir_threshold 파인튜닝 또는 dist_pct_min 재검토)
