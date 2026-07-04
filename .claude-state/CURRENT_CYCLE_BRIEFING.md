# Current Cycle Briefing

_Last updated: 2026-07-04 (Cycle 395 완료)_

## 현재 상태

- **완료된 사이클**: 395
- **다음 사이클**: 396 (396 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **price_cluster**: Sh=1.06(atr_bounce_factor=0.5 확정), Consist=2/8 → 최적화 완전 종료
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8520개 (+4)

## Cycle 395 주요 결과

### A(품질): BacktestEngine 경계값 테스트 2개 추가

- `tests/test_backtest_engine.py`: test_atr_zero_skips_signal_adds_fail_reason
  - ATR=0 DataFrame에서 신호 스킵 + fail_reasons에 "atr=0 skipped" 기록 검증
- `tests/test_backtest_engine.py`: test_small_initial_balance_engine_no_crash
  - initial_balance=$1 극소 잔고에서 엔진 크래시 없음 (size≈0 경계값)

### C(데이터): feed.py 지표 일관성 테스트 2개 추가

- `tests/test_feed_boundary.py`: test_bb_width_non_negative_for_normal_prices
  - 정상 가격 데이터에서 bb_width >= 0 (bb_upper >= bb_lower) 검증
- `tests/test_feed_boundary.py`: test_macd_hist_equals_macd_minus_signal
  - macd_hist = macd - macd_signal 수식 일관성 (atol=1e-10)

### F(리서치): atr_bounce_factor 탐색 완전 종료 + price_cluster 최적화 종료

- atr_bounce_factor=0.3 실험: Sh=0.07 DEAD (동적threshold<baseline→노이즈)
- atr_bounce_factor=0.5 실험: Sh=1.06(+0.11↑), SharpeStd=1.67(2.20→↓안정화), Consistency=2/8 유지
- **확정 파라미터**: atr_bounce_factor=0.5 (paper_sim 업데이트)
- **price_cluster 최적화 완전 종료**: Consistency ceiling=2/8 구조적 한계 확인

## 다음 사이클 396 우선순위

1. **B(리스크)**: DrawdownMonitor/CircuitBreaker 미커버 케이스 추가
2. **D(ML)**: dema_cross WFO 그리드 현행화 또는 roc_ma_cross SL/TP 실험
3. **F(리서치)**: dema_cross PF 1.38→1.50 달성 방법 분석 또는 roc_ma_cross 추가 개선 탐색
