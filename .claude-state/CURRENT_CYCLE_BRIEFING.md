# Current Cycle Briefing

_Last updated: 2026-07-08 (Cycle 404 완료)_

## 현재 상태

- **완료된 사이클**: 404
- **다음 사이클**: 405 (405 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44, Trades=65, 0/8 Consistency — 탐색 완전 종료
- **price_cluster**: Sh=1.06, PF=1.32, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38, Consist=2/8 → 탐색 완전 종료
- **positional_scaling**: Sh=-0.38, PF=1.09, Consist=1/8 → 파라미터화 필요, 탐색 보류
- **Bundle OOS**: 5/5 PASS (2026-07-08, 실 BTC CSV 4h 재샘플링)
- **전체 테스트 수**: 8622개 (+6 this cycle)

## Cycle 404 주요 결과

### D(ML): select_features_pfi() 엣지케이스 (3개 추가)

- `tests/test_ml_pipeline_edge_cases.py` (TestSelectFeaturesPfi):
  - `test_select_features_pfi_small_xtrain_no_crash`: X_train 20행(<100) → n_repeats=10 경로, 크래시 없이 피처 반환
  - `test_select_features_pfi_top_k_exceeds_feature_count`: top_k=20, 피처=3 → k=3, 전체 반환
  - `test_select_features_pfi_top_k_one_enforces_minimum`: top_k=1, 피처=3 → k=2, 최소값 강제

### E(실행): PaperConnector 포지션 state (3개 추가)

- `tests/test_exchange.py` (TestPaperConnectorCycle404):
  - `test_open_positions_after_buy`: buy 후 open_positions[BTC/USDT] > 0 검증
  - `test_open_positions_cleared_after_sell`: buy→sell 후 qty=0 검증
  - `test_timeout_order_does_not_modify_position`: timeout_prob=1.0 → 잔고/포지션 불변

### F(리서치): engulfing_zone / volatility_cluster Bundle OOS 후보 검토

- **engulfing_zone BTC 1h 전체**: Sh=-0.79, PF=0.93, Trades=657, MDD=52.5% → 구조적 실패
  - 657 trades (1h) = 과도한 신호 생성, noise 거래 비율 높음
  - BTC 4h: Sh=-2.74, MDD=44.9% → 더 나쁨, Bundle OOS 후보 완전 부적합
- **volatility_cluster BTC 4h**: Sh=0.32, PF=1.06, MDD=12.2%
  - MDD 양호하지만 Sh/PF PASS 기준 미달 → Bundle OOS 6번째 후보 불가
- **결론**: Bundle OOS 신규 후보 현재 없음, 기존 5/5 강화 집중

## 다음 사이클 (405): A+C+F

- **A(품질)**: BacktestEngine 극단 슬리피지/커미션 케이스 또는 optimize_roc_ma_cross() 미커버 케이스
- **C(데이터)**: DataFeed/feed_boundary rsi14 NaN, bb_upper/lower 관계 미커버 케이스
- **F(리서치)**: lob_maker 구조 분석 (rank 5, Sh=-0.04, Trades=75) — 파라미터화 가능성 탐색
