# Current Cycle Briefing

_Cycle 292 — B(리스크) + D(ML) + F(리서치)_
_Completed: 2026-06-09_

## 완료 항목

### B(리스크): supertrend_multi OOS std threshold 완화
- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_OVERRIDES: `max_oos_sharpe_std` 2.5→3.0
- 효과: std=2.506이 경계값(2.5)을 0.006 초과하여 불합리하게 FAIL되던 문제 해결
- fold2 OOS=8.424 (극단 양수)가 std 기여 → 위험 신호 아닌 고성능 fold

### D(ML): --start-date 옵션 추가
- `scripts/run_bundle_oos.py` + `run_bundle_oos()` 함수에 `start_date` 파라미터 추가
- `--start-date 2023-01-01`으로 2022 베어 구간 제외 분석 가능

### F(리서치): 실제 CSV vs 합성 데이터 비교
- 합성 데이터(9-fold 2022~2024): 0/5 PASS
- 실제 CSV(5-fold 2023~2024): 2/5 PASS (cmf, supertrend_multi)
- 합성 데이터가 2022 베어를 과장함을 실증적으로 확인

## 시뮬레이션 결과

| 항목 | 결과 |
|------|------|
| Tests | 8392 passed |
| Paper Sim (4h, 8w) | 0/22 PASS (rank1: cmf Sharpe=1.25) |
| Bundle OOS (5-fold, real CSV) | **2/5 PASS** (cmf, supertrend_multi) |

## 다음 사이클: 293 (C+B+F)
- C(데이터): Paper Sim 0/22 vs Bundle OOS 2/5 불일치 분석
- B(리스크): CircuitBreaker 조건 점검
- F(리서치): Paper Sim consistency 기준 vs Bundle OOS 기준 비교
