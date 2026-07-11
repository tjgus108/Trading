# Current Cycle Briefing

_Last updated: 2026-07-11 (Cycle 414 완료)_

## 현재 상태

- **완료된 사이클**: 414
- **다음 사이클**: 415 (415 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **narrow_range**: Sh=-0.51, PF=0.97(<1.0), Tr=46, 0/8 → 구조적 실패 재확정 (Cycle414 F - atr_mult/range_lookback 파라미터화 불가)
- **positional_scaling**: Sh=-0.38, PF=1.09, Tr=34, 1/8 → 구조적 실패 확정 (pullback==rally 동일 조건)
- **momentum_quality**: Sh=-1.19, PF=0.96(<1.0), Tr=71, 1/8 → 구조적 실패 확정 (DEAD PARAM + RANGING)
- **volume_breakout**: Sh=-0.74, PF=0.96(<1.0), Tr=72, 0/8 → 구조적 실패 확정
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-11 재확인, BTC CSV 4h) — SSL fallback
- **전체 테스트 수**: 8694 총계 (8671 passed + 23 skipped) — Cycle414 +9 추가

## Cycle 414 주요 결과

### D(ML): optimize_donchian + select_features_pfi 경계값 (6개 추가)
1. `test_optimize_donchian_returns_wf_result`: optimize_donchian() → WalkForwardResult 타입 검증
2. `test_optimize_donchian_strategy_name_is_donchian`: strategy_name == 'donchian_breakout'
3. `test_optimize_donchian_oos_sharpe_std_non_negative`: oos_sharpe_std >= 0.0
4. `test_single_feature_returns_non_empty`: X_train 1개 피처 → 리스트 반환 (경계값)
5. `test_small_sample_below_100_no_crash`: 60행 소표본 → n_repeats=10 경로 검증
6. `test_top_k_limits_output_count`: top_k=2, 5피처 → 반환 수 ≤ 2

### E(실행): PaperConnector 미커버 케이스 (3개 추가)
7. `test_fee_deducted_on_round_trip`: fee_rate=0.001 → 동일가격 buy+sell 후 balance < 초기
8. `test_wait_for_fill_returns_symbol_field`: wait_for_fill() 결과에 symbol 키 존재/값 검증
9. `test_reset_after_multiple_trades_restores_balance`: 6회 거래 후 reset → 초기 완전 복원

### F(리서치): narrow_range BTC 1h 구조적 한계 재확정
- Sh=-0.51, PF=0.97(<1.0), Trades=46, MDD=10.1%, 0/8 Consistency, SharpeStd=1.48
- RANGING 47.3%: NR 바 빈발 + ATR 축소 조건 과다 충족 → BUY/SELL 돌파 후 즉각 reversal
- atr_mult 파라미터화: atr_threshold 강화해도 RANGING에서 ATR 이미 낮아 에지 개선 불가
- range_lookback(nr_lookback) 강화: NR7도 RANGING에서 빈발 → BUY/SELL 대칭성 유지
- walk_forward.py DEFAULT_GRIDS["narrow_range"] 주석에 Cycle414 재확정 추가

## 다음 사이클 415 방향 (A+C+F)

- **A(품질)**: BacktestEngine 또는 apply_wfe 미커버 케이스 (test_backtest_engine.py)
- **C(데이터)**: DataFeed 미커버 지표 경계값 (test_feed_boundary.py) - rsi14, donchian, vwap 등
- **F(리서치)**: dema_cross PF 1.38→1.50 gap 재검토 (탐색 종료 재확인) 또는 lob_maker 구조 재분석
