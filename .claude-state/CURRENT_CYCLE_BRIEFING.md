# Current Cycle Briefing

_Last updated: 2026-07-04 (Cycle 394 완료)_

## 현재 상태

- **완료된 사이클**: 394
- **다음 사이클**: 395 (395 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8516개 (+2 명시적, 수집총계 8539)

## Cycle 394 주요 결과

### D(ML): WFO 그리드 개선 + atr_bounce_factor 세밀 탐색 추가

- `src/backtest/walk_forward.py`: price_cluster STRATEGY_PARAM_GRIDS 트리밍
  - close_window: [50,60] → [50] (60 DEAD 확정)
  - vol_atr_trend_min: [1.0,1.2,1.5,2.0,2.5] → [1.2] (1.0 DEAD, 나머지 열세)
  - bounce_pct: [0.006,0.008,0.010,0.020,0.025] → [0.006,0.008,0.010] (구형 제거)
  - atr_bounce_factor: [0.0,1.0] → [0.0,0.3,0.5,1.0] (중간값 추가)

### E(실행): PaperTrader edge case 테스트 2개 추가

- `tests/test_paper_trader.py`: test_execution_summary_single_trade_avg_fill_time_zero
  - 거래 1건 시 avg_fill_time=0.0 (len<2 → 구간 없음) 검증
- `tests/test_paper_trader.py`: test_tiered_slippage_large_order_small_cap_higher_than_large_cap
  - $40k 대형 주문에서 SHIB(small) >> BTC(large) slippage 차이 정량 검증

### F(리서치): price_cluster 분석 + 4h/1h 타임프레임 패턴 관찰

- price_cluster 기준선 복원 확인: Sh=0.95, PF=1.33, Tr=34, Consistency=2/8 (FAIL)
- atr_bounce_factor [0.3, 0.5] 추가 → 다음 WFO 결과로 최적화 종료 여부 결정
- 4h OOS 5/5 PASS vs 1h 1/19 PASS → 4h 타임프레임 우수성 지속 확인

## 시뮬레이션 결과

### Paper Sim (1h WFO, Cycle394)

| 전략 | Sharpe | PF | Trades | Consistency | Pass |
|------|--------|-----|--------|-------------|------|
| price_cluster | 0.95 | 1.33 | 34 | 2/8 | FAIL |
| roc_ma_cross | 1.81 | 2.02 | 14 | 4/8 | PASS |

### Bundle OOS (4h, 캐시 유지)

| 전략 | Sharpe | PF | Consistency | Pass |
|------|--------|-----|-------------|------|
| order_flow_imbalance_v2 | 4.35 | 1.94 | 80% | PASS |
| supertrend_multi | 3.89 | 2.74 | 80% | PASS |
| value_area | 3.07 | 1.77 | 40% | PASS |
| vwap_cross | 3.05 | 1.92 | 80% | PASS |
| cmf | 2.51 | 1.39 | 100% | PASS |
