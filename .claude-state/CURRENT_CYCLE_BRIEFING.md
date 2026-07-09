# Current Cycle Briefing

_Last updated: 2026-07-09 (Cycle 408 완료)_

## 현재 상태

- **완료된 사이클**: 408
- **다음 사이클**: 409 (409 mod 5 = 4 → D+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정 (iloc[::4] HTF proxy 불정확, 탐색 금지)
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정 (음의 엣지, 탐색 금지)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정, 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8648 총계 (8625 passed + 23 skipped) — Cycle408 +6 추가

## Cycle 408 주요 결과

### C(데이터): DataFeed 지표 경계값 테스트 (3개 추가)

- `tests/test_feed_boundary.py` (TestIndicatorBoundaryC408):
  - `test_ema200_lags_ema20_on_sudden_spike`: 급등 시 ema200이 ema20보다 close와 멀어야 함
  - `test_bb_width_zero_for_constant_close`: 상수 가격 → std=0 → bb_width=0 수학 검증
  - `test_macd_hist_positive_in_sustained_uptrend`: 단조 상승 → macd_hist > 0 (fast EMA > slow EMA lag)

### B(리스크): get_size_multiplier 복합 케이스 (3개 추가)

- `tests/test_drawdown_monitor.py`:
  - `test_atr_elevated_and_mdd_warn_compound`: ATR elevated(0.5x) + MDD WARN(0.5x) → min=0.5
  - `test_get_size_multiplier_all_four_factors_compound`: streak+WARN+ATR+Sharpe decay 4인자 → min=0.5
  - `test_trend_down_regime_does_not_change_daily_limit`: TREND_DOWN 일일 한도 3% 유지 검증

### F(리서치): htf_ema 1h BTC 구조적 실패 확정

- BTC 1h: Sh=-0.72, **PF=0.91(<1.0=음의 엣지)**, Trades=43, Consistency=0/8
- 근본 원인 1: iloc[::4] 다운샘플링 = 실제 4h 캔들 불일치 (EMA 값이 real 4h EMA와 다른 proxy)
- 근본 원인 2: BTC 1h RANGING 47.3% → EMA9 크로스 양방향 빈발 → 차단 불가
- 파라미터화 가능 요소 없음 (span=21, ema9=9, rsi thresh 하드코딩)
- 결론: htf_ema 추가 탐색 금지 → `src/backtest/walk_forward.py` DEFAULT_GRIDS["htf_ema"]={} 추가

## 다음 사이클 (409): D+E+F (409 mod 5 = 4 → D+E+F)

- **D(ML)**: WalkForwardTrainer 또는 optimize_* 함수 미커버 경계 케이스
- **E(실행)**: PaperConnector 또는 BacktestEngine 미커버 케이스
- **F(리서치)**: price_action_momentum (rank 14, Sh=-1.08, Tr=73) 또는 relative_volume 구조 분석
