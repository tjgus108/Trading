# Current Cycle Briefing

_Last updated: 2026-07-08 (Cycle 405 완료)_

## 현재 상태

- **완료된 사이클**: 405
- **다음 사이클**: 406 (406 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44, Trades=65, 0/8 Consistency — 탐색 완전 종료
- **price_cluster**: Sh=1.06, PF=1.32, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38, Consist=2/8 → 탐색 완전 종료
- **positional_scaling**: Sh=-0.38, PF=1.09, Consist=1/8 → 파라미터화 필요, 탐색 보류
- **lob_maker**: Sh=-0.04, PF=1.05, Consist=0/8 → 탐색 완전 종료 (proxy OFI/VPIN 구조적 한계)
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링)
- **전체 테스트 수**: 8628개 (+6 this cycle)

## Cycle 405 주요 결과

### A(품질): BacktestEngine 극단 슬리피지/커미션 케이스 (3개 추가)

- `tests/test_backtest_engine.py`:
  - `test_extreme_slippage_no_crash`: slippage=1.0 극단값 → 크래시 없음, BacktestResult 반환
  - `test_extreme_commission_no_crash`: commission=0.5 극단값 → 크래시 없음, total_fees>0
  - `test_extreme_slippage_cost_greater_than_normal`: slippage=1.0 > 0.001 슬리피지 비용 검증

### C(데이터): DataFeed 지표 엣지케이스 (3개 추가)

- `tests/test_feed_boundary.py` (TestIndicatorEdgeCases405):
  - `test_rsi14_first_row_nan`: 30행 데이터 → rsi14 첫 행 NaN (close.diff() 첫 delta=NaN)
  - `test_bb_upper_geq_bb_lower_direct`: 50행 데이터 → bb_upper >= bb_lower 항상 성립
  - `test_volume_zero_volume_quote_zero`: volume=0 캔들 → volume_quote=volume×close=0

### F(리서치): lob_maker 구조 분석 → 탐색 완전 종료

- **근본 원인**: proxy OFI = (close-open)/(high-low) — 실거래소 Order Book 없음
- VPIN: VPINCalculator(OHLCV 기반) — 실제 order flow toxicity 계산 불가
- BTC Sh=-0.04, ETH Sh=-0.90, SOL Sh=-0.73 (모두 음수 일관)
- **결론**: 실거래소 LOB 데이터 없이 구조적 개선 불가. 파라미터 탐색도 의미 없음.

### 코드 개선 2건

1. `scripts/paper_simulation.py` line~124: 중복 key `"price_cluster"` dead entry 제거 (버그픽스)
2. `scripts/paper_simulation.py`: lob_maker 탐색 종료 결론 주석 추가

## 다음 사이클 (406): B+D+F

- **B(리스크)**: CircuitBreaker 또는 KellySizer 미커버 엣지케이스 3개
- **D(ML)**: WalkForwardTrainer.train() 또는 ML 파이프라인 미커버 케이스 3개
- **F(리서치)**: 1h paper_sim 미탐색 전략 구조 분석 또는 Bundle OOS cmf(score=25.0) 강화 탐색
