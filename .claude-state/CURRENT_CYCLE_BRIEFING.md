# Current Cycle Briefing

_Last updated: 2026-07-11 (Cycle 415 완료)_

## 현재 상태

- **완료된 사이클**: 415
- **다음 사이클**: 416 (416 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **price_cluster**: Sh=1.06, PF=1.32, Tr=35, 2/8 → 2/8 ceiling 구조적 한계 확정 (Cycle415 F)
- **dema_cross**: Sh=0.85, PF=1.38, Tr=26, 2/8 → 탐색 완전 종료 (Cycle377 F)
- **frama**: Sh=0.44, PF=1.11, Tr=65, 0/8 → 탐색 종료 (RANGING 47.3% weak_signal 차단)
- **narrow_range**: Sh=-0.51, PF=0.97(<1.0), Tr=46, 0/8 → 구조적 실패 확정
- **positional_scaling**: Sh=-0.38, PF=1.09, Tr=34, 1/8 → 구조적 실패 확정 (pullback==rally)
- **momentum_quality**: Sh=-1.19, PF=0.96(<1.0), Tr=71, 1/8 → 구조적 실패 확정
- **volume_breakout**: Sh=-0.74, PF=0.96(<1.0), Tr=72, 0/8 → 구조적 실패 확정
- **relative_volume**: Sh=-0.99, PF=0.92(<1.0), Tr=64, 0/8 → 구조적 실패 확정
- **price_action_momentum**: Sh=-1.08, PF=0.97(<1.0), Tr=73, 1/8 → 구조적 실패 확정
- **htf_ema**: Sh=-0.72, PF=0.91(<1.0), Tr=43, 0/8 → 구조적 실패 확정
- **acceleration_band**: Sh=-0.94, PF=0.98(<1.0), Tr=44, 1/8 → 구조적 실패 확정
- **lob_maker**: Sh=-0.04, Trades=75, MDD=17%, 0/8 → 구조적 한계 확정 (LOB 데이터 없음)
- **Bundle OOS**: 5/5 PASS (2026-07-08 실거래소 데이터 기준, SSL 차단으로 신규 실행 불가)
- **전체 테스트 수**: 8700 총계 (8677 passed + 23 skipped) — Cycle415 +6 추가

## Cycle 415 주요 결과

### A(품질): apply_wfe 미커버 3케이스 추가
1. `test_apply_wfe_below_min_wfe_sets_fail_and_not_passed`: IS>0, 0<wfe<0.5 → fail_reasons+passed=False
2. `test_apply_wfe_is_exactly_neg1_boundary_gives_wfe1`: IS=-1.0 경계 → wfe=1.0 (소폭 음수 브랜치)
3. `test_apply_wfe_oos_exactly_1p5_when_is_strong_neg_gives_zero`: IS=-2.0, OOS=1.5 → wfe=0.0 (경계)

### C(데이터): feed 지표 경계값 3케이스 추가 (TestIndicatorBoundaryC415)
4. `test_rsi14_bounded_0_to_100`: 진동 가격 50행 → rsi14 비NaN [0,100] 범위 검증
5. `test_donchian_high_gte_donchian_low`: 50행 → donchian_high >= donchian_low (비NaN 쌍)
6. `test_vwap_equals_close_for_constant_ohlcv`: 상수 OHLCV → vwap = close (수학적 일관성)

### F(리서치): price_cluster 2/8 Consistency ceiling 구조적 원인 확정
- avg Sh=1.06, PF=1.32, Trades=35, SharpeStd=1.67 → PF<1.5가 binding constraint
- PASS 구간: 2023 Q2(BTC 25k-31k 횡보) + 2023 Q4(Oct 펌프 공고화) — 진성 RANGING
- FAIL 구간: 2023 H1 상승(15k→30k), 2024 H1 상승(40k→60k) — TREND_UP에서 cluster sweep
- vol_regime_filter=True로도 TREND_UP 일부 신호 발생 → PF<1.5 구조적 불가피
- walk_forward.py atr_bounce_factor [0.0,0.3,0.5,1.0] → [0.5] 단일값 (75% 그리드 감소, 72→18 combos)
- price_cluster 추가 파라미터 탐색 완전 종료. 보조 전략으로 보존.

## 다음 사이클 416 방향 (B+D+F)

- **B(리스크)**: DrawdownMonitor 또는 CircuitBreaker 미커버 케이스
- **D(ML)**: optimize_donchian 또는 select_features_pfi 추가 경계값
- **F(리서치)**: roc_ma_cross AvgTrades=14 경계 분석 (PASS 4/8 구간 조건 파악)
