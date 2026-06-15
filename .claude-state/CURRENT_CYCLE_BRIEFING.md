# Current Cycle Briefing

_Cycle 312 | 2026-06-15 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): kelly_fraction_multiplier 테스트 커버리지 추가
- `tests/test_risk.py`에 `TestKellyFractionMultiplier` 클래스 신규 추가 (4개 테스트)
- 확인 사항: kelly_reduce_at_mdd=0.08 기준 적절함 (mdd_warn < kelly_reduce < mdd_block)
- 총 **8404 passed, 23 skipped**

### D(ML): narrow_range nr_lookback 실험 (5→4)
- 실험 결과: NR4 = NR5와 동일한 trade 빈도 (8, 10, 10, 9, 10)
- 결론: binding constraint = ATR_THRESHOLD / VOL_SPIKE_MULT / NR_SCAN_WINDOW
- BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"] 복원: nr_lookback 명시 제거

### F(리서치): TRAIN_HOURS 축소 실험 (210→84일)
- 가설 A: 84일 train → 12 windows 생성 성공, 그러나 성능 악화
- price_cluster consistency: 3/8→1/12 폭락 (파라미터 최적화 데이터 부족)
- TRAIN_HOURS 210일 복원

## 시뮬레이션 결과

**Paper Sim (84일 train, 12 windows)**:
- 0/22 PASS
- rank1: supertrend_multi (3/12, AvgSharpe=0.13, AvgPF=1.12)
- rank2: price_cluster (1/12, AvgSharpe=0.19, AvgPF=1.10)

**Bundle OOS (5-fold, nr_lookback=4 실험)**:
- 2/5 PASS (cmf, supertrend_multi)
- narrow_range: avg_oos_sharpe=-0.194 (FAIL) — nr_lookback=5와 동일

## 현재 설정

- `paper_simulation.py`: TRAIN_HOURS=24*210 (복원), TEST_HOURS=24*60
- `run_bundle_oos.py`: narrow_range = `{trend_regime_filter: False, ema_slope: 0.0}`
- 테스트: 8404 passed (이전 8400 + 4개 신규)

## 다음 사이클 (313) 예정

- C(데이터): NR_SCAN_WINDOW 3→5 실험 (binding constraint 완화)
- B(리스크): check_strategy_health() 테스트 확인
- F(리서치): 1h PF 개선 방향 분석
