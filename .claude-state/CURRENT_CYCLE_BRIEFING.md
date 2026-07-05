# Current Cycle Briefing

_Last updated: 2026-07-05 (Cycle 399 완료)_

## 현재 상태

- **완료된 사이클**: 399
- **다음 사이클**: 400 (400 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44(+0.20), PF=1.11, Trades=65(+63%) → sell_min=60 격리, buy_max=50 단독 검증 예정
- **Bundle OOS**: 5/5 PASS (최신)
- **전체 테스트 수**: 8556개 (+12)

## Cycle 399 주요 결과

### D(ML): MLSignalGenerator 엣지케이스 6개 추가

- `tests/test_ml_pipeline_edge_cases.py`: `TestMLSignalGeneratorAdvanced` 클래스 추가
  - benchmark_stats empty/recorded 검증
  - load() trained_regime 자동 regime_aware 활성화
  - feature_names mismatch → zero-fill reindex
  - get_feature_importances top_n 잘라내기
  - get_low_importance_features threshold 필터링

### E(실행): PaperTrader 미커버 경로 6개 추가

- `tests/test_paper_trader.py`: 6 tests 추가
  - zero price/quantity → rejected 반환
  - kelly_sizer compute_dynamic=0.0 → 원래 수량 유지
  - kelly record_trade exception → crash 없이 filled
  - vol_targeting adjust exception → crash 없이 filled
  - execution_summary win_rate 계산 검증 (2승1패=0.667)

### F(리서치): frama weak_rsi_buy_max=50 sell_min 격리 실험

- Cycle398 혼재 실험 분석: buy_max=50 + sell_min=50 동시 변경
  - Sh=0.44(+0.20), Trades=65(+63%) → 방향 유효
  - Consist=0/8 → sell_min 변경이 일관성 해침
- Cycle400 격리 실험 준비: sell_min=60 고정, buy_max=50 단독 효과 검증
- `scripts/paper_simulation.py`: `weak_rsi_sell_min=60` 복원 완료

## 시뮬레이션 현황 (Cycle 399 생성, buy_max=50+sell_min=50 혼재)

| 전략 | Sharpe | PF | Trades | Consist | Pass |
|------|--------|-----|--------|---------|------|
| roc_ma_cross | 1.81 | 2.02 | 14 | 4/8 | **PASS** |
| frama | 0.44 | 1.11 | 65 | 0/8 | FAIL (격리 실험 필요) |
| price_cluster | 1.06 | 1.32 | 35 | 2/8 | FAIL |
| dema_cross | 0.85 | 1.38 | 26 | 2/8 | FAIL |

## Cycle 400 작업 방향 (400 mod 5 = 0 → A+C+F)

- **A(품질)**: BacktestEngine/WFO coverage 강화
- **C(데이터)**: feed.py coverage 보완
- **F(리서치)**: frama buy_max=50 단독 효과 검증 (sell_min=60 격리)
