# Current Cycle Briefing

_Last updated: 2026-07-10 (Cycle 411 완료)_

## 현재 상태

- **완료된 사이클**: 411
- **다음 사이클**: 412 (412 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **volume_breakout**: Sh=-0.74, PF=0.96(<1.0), Tr=72, 0/8 → 구조적 실패 확정 (SL 없음+spike 1.5x 과다+RANGING)
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정 (RANGING 볼륨 노이즈, 탐색 금지)
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정 (모멘텀 vs RANGING 부조화, 탐색 금지)
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정 (iloc[::4] HTF proxy 불정확, 탐색 금지)
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정 (음의 엣지, 탐색 금지)
- **narrow_range**: Sh=-0.51, PF=0.97, Tr=46, 0/8 → 구조적 한계 확정, 탐색 보류
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음), 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링) — SSL fallback으로 갱신 불가, 보존
- **전체 테스트 수**: 8667 총계 (8644 passed + 23 skipped) — Cycle411 +6 추가

## Cycle 411 주요 결과

### B(리스크): DrawdownMonitor transition_cushion + set_regime 복합 케이스 (3개 추가)
1. `test_transition_cushion_disabled_by_default_returns_one`: disabled(기본값) → confidence 무관 1.0
2. `test_transition_cushion_enabled_crisis_regime_compound`: CRISIS+cushion 활성+낮은confidence → 일일한도2%+cushion0.5x 복합
3. `test_get_size_multiplier_atr_and_sharpe_decay_no_streak_mdd`: ATR(0.5x)+SharpeDecay(0.5x), streak/MDD 없음 → min=0.5

### D(ML): optimize 함수 strategy_name + best_params 키 검증 (3개 추가)
4. `test_optimize_frama_strategy_name_is_frama`: strategy_name == "frama" 필드 검증
5. `test_optimize_dema_cross_best_params_contains_bb_width_min_filter`: best_params에 bb_width_min_filter 키 검증
6. `test_optimize_narrow_range_strategy_name_is_narrow_range`: strategy_name == "narrow_range" 검증

### F(리서치): volume_breakout BTC 1h 구조적 한계 확정
- Sh=-0.74, PF=0.96(<1.0), Trades=72, 0/8 — 음의 엣지 확정
- 근본 원인 1: _SPIKE_MULT=1.5 하드코딩 + SL 파라미터 없음 → MDD 22.1% > 20% 한계
- 근본 원인 2: EMA50 추세 필터가 신호 조건이 아닌 confidence에만 사용
- walk_forward.py DEFAULT_GRIDS["volume_breakout"]={} 추가 (구조적 한계 주석)

## 다음 사이클: 412 (B+D+F)

- B(리스크): CircuitBreaker 미커버 시나리오 또는 DrawdownMonitor rolling_mdd/trailing_stop 케이스
- D(ML): WalkForwardTrainer.train() feature_selection 경로 또는 optimize 함수 추가 필드 검토
- F(리서치): momentum_quality (rank 10, Sh=-1.19, Trades=71, 1/8) 구조 분석
