# Current Cycle Briefing

_Last updated: 2026-07-09 (Cycle 407 완료)_

## 현재 상태

- **완료된 사이클**: 407
- **다음 사이클**: 408 (408 mod 5 = 3 → C+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0!), Tr=44, 1/8 → 구조적 실패 확정 (RANGING 47.3%, false breakout), 탐색 금지
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정 (1h BTC 노이즈), 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8641 총계 (8618 passed + 23 skipped) — Cycle407 +7 추가

## Cycle 407 주요 결과

### B(리스크): CircuitBreaker 복합 케이스 테스트 (3개 추가)

- `tests/test_circuit_breaker.py`:
  - `test_total_drawdown_and_atr_surge_drawdown_wins`: total_dd(16%)>limit(15%) + ATR surge 동시 → triggered=True, reason='전체' (드로우다운 우선, ATR surge 숨김)
  - `test_reset_daily_does_not_clear_consecutive_loss_cooldown`: reset_daily() 후 cooldown_remaining=3 유지 (일일 상태만 초기화)
  - `test_to_dict_from_dict_preserves_rapid_decline_cooldown`: 직렬화 라운드트립 후 rapid_decline_cooldown=5 보존

### D(ML): optimize_frama() / optimize_narrow_range() 엣지케이스 (4개 추가)

- `tests/test_phase_d.py`:
  - `TestOptimizeFrama.test_optimize_frama_avg_oos_sharpe_is_float`: avg_oos_sharpe float 타입
  - `TestOptimizeFrama.test_optimize_frama_oos_sharpe_std_non_negative`: oos_sharpe_std >= 0.0
  - `TestOptimizeNarrowRange.test_optimize_narrow_range_single_window_no_crash`: n_windows=1, strategy_name='narrow_range' 확인
  - `TestOptimizeNarrowRange.test_optimize_narrow_range_result_fields`: 필드 타입/속성 완전 검증

### F(리서치): acceleration_band 1h BTC 구조적 실패 분석 완료

- **BTC 1h**: rank15, Sh=-0.94, PF=0.98(<1.0!), Trades=44, MDD=13%, 1/8 Consistency
- 근본 원인: Headley Acceleration Band 상향돌파 → RANGING 47.3% 지배 → false breakout 다수
  - upper band cross 후 mean reversion이 지배적 → PF<1.0 구조적 손실
- ETH 1h: Sh=-2.03, PF=0.57, Trades=13(<15) — ATR 2.12% → 밴드 폭 과대 → 신호 부족
- SOL 1h: Sh=-0.80, PF=1.00, Trades=11(<15) — ATR 3.17% → 신호 부족
- 결론: acceleration_band 1h 구조적 실패. 추가 탐색 금지.
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["acceleration_band"] 구조적 실패 주석 추가

## 다음 사이클 (408): C+E+F

- **C(데이터)**: DataFeed / WebSocket 엣지케이스 (OHLCV 보정, NaN 전파 방지)
- **E(실행)**: PaperConnector / SlippageModel 엣지케이스 (adaptive_slippage high 레짐, 포지션 전환)
- **F(리서치)**: dema_cross 1h BTC 분석 (rank4, Sh=0.85, PF=1.38, gap=0.12 → DEMA 기간 파라미터 탐색 여지)
