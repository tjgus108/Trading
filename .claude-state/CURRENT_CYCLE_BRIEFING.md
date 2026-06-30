# Current Cycle Briefing

_Last updated: 2026-06-30 (Cycle 373 완료)_

## 현재 상태

- **완료된 사이클**: 373
- **다음 사이클**: 374 (374 mod 5 = 4 → D+E+F)
- **연속 PASS 실패**: 58연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 373 주요 결과

### C(데이터): feed.py 피처 추가 + enrich_indicators 동기화
- `bb_width` = (bb_upper - bb_lower) / sma20 추가 (BB 폭 비율, squeeze 탐지)
- `macd_hist` = macd - macd_signal 추가 (MACD 히스토그램, 모멘텀 강도/방향)
- `scripts/paper_simulation.py` enrich_indicators()에도 동기화 (누락 버그 수정)

### B(리스크): transition_cushion 직렬화/역직렬화 테스트 4개 추가
- `test_transition_cushion_to_dict_includes_fields`
- `test_transition_cushion_from_dict_roundtrip`
- `test_transition_cushion_multiplier_after_restore` (< threshold → 0.5, >= → 1.0)
- `test_transition_cushion_disabled_default_after_restore` (항상 1.0)
- 결과: 8453 passed (+4)

### F(리서치): macd_hist_filter dead param 확정
- dema_cross에 `macd_hist_filter` 파라미터 추가 구현
- 실험 결과: Sh=0.80, PF=1.38, Trades=30 → **기존과 동일** → dead param
- 원인: DEMA cross (fast=8/slow=20)와 MACD hist 높은 상관관계 → cross 시점에 hist이미 같은 방향
- **결론**: macd_hist_filter 탐색 종료. 코드 보존 (다른 전략용), 기본값 False

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/data/feed.py` | `macd_hist`, `bb_width` 추가 (C) |
| `scripts/paper_simulation.py` | enrich_indicators에 `macd_hist`, `bb_width` 추가 + 실험 후 복원 (C+F) |
| `src/strategy/dema_cross.py` | `macd_hist_filter=False` 파라미터 + 필터 로직 (F) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS + factory에 `macd_hist_filter` 추가 (F) |
| `tests/test_drawdown_monitor.py` | transition_cushion 테스트 4개 추가 (B) |

## Cycle 374 예고 (374 mod 5 = 4 → D+E+F)

- **D(ML)**: dema_cross BB width squeeze 필터 실험 (`bb_width_min` threshold)
  - BTC 1h bb_width 분포 분석 → threshold 설정 → paper_sim 실험
- **E(실행)**: macd_hist/bb_width 열 PaperConnector 데이터 흐름 확인
- **F(리서치)**: avg_win/avg_loss 비율 분석 → stop-loss 개선 방향 탐색
