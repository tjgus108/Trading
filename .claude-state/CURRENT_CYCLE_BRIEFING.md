# Current Cycle Briefing

_Last updated: 2026-07-06 (Cycle 399 완료)_

## 현재 상태

- **완료된 사이클**: 399
- **다음 사이클**: 400 (400 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44(↑0.24), Trades=65(↑40) — weak_rsi_buy_max=50 확정
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (2026-07-04)
- **전체 테스트 수**: 8556개 (+12)

## Cycle 399 주요 결과

### D(ML): MLSignalGenerator benchmark_stats/feature_importance 미커버 케이스 6개

- `tests/test_ml_pipeline_edge_cases.py`: `TestMLSignalGeneratorBenchmarkStats` 클래스 (3 tests)
  - benchmark_stats 초기 상태, 누적 카운트, reset 검증
- `tests/test_ml_pipeline_edge_cases.py`: `TestMLSignalGeneratorFeatureImportance` 클래스 (3 tests)
  - get_feature_importances, feature_importance_report, get_low_importance_features 모델 미로드 케이스

### E(실행): PaperTrader 미커버 케이스 6개

- `tests/test_paper_trader.py`: execute_signal 엣지케이스 3개 (unknown_action/zero_price/zero_qty)
- `tests/test_paper_trader.py`: get_summary 및 reset() 3개 (open_position_value/no_sells/reset)

### F(리서치): frama weak_rsi_buy_max=50 결과 분석

- BTC 1h paper_sim: Sh=0.44(↑0.24+83%), Trades=65(↑40+62.5%), PF=1.11, 0/8 Consistency
- **결론**: weak_rsi_buy_max=50 > 40 확정. paper_sim 설정 50 유지.
- 0/8 Consistency는 frama 구조적 한계 — 파라미터 변경으로 해결 불가
- WFO 그리드 [40,50,60] 유지 — 다음 사이클에서 60도 실험 예정

## 다음 사이클 (400): A+C+F

- **A(품질)**: BacktestEngine 또는 WalkForward optimize_frama() 엣지케이스
- **C(데이터)**: DataFeed/feed.py 미커버 케이스
- **F(리서치)**: frama WFO 그리드 결과 분석, weak_rsi_sell_min 탐색 방향
