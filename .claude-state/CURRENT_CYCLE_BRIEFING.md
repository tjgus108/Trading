# Current Cycle Briefing

_Cycle 311 | 2026-06-14 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): Paper Simulation 슬리피지 레짐 리포트 추가
- `scripts/paper_simulation.py` window_results에 `slippage_regime_counts` 추가
- 결과 dict에 `slippage_regime_agg` 추가, generate_report()에 슬리피지 레짐 분포 섹션 추가
- 결과: price_cluster MDD=12.2%의 high regime 비율이 낮음 (정상) → slippage가 MDD 원인 아님 확인

### D(ML): narrow_range ema_slope 버그 수정 + 실험 결과 분석
- **버그**: `run_bundle_oos.py` `enrich_indicators()`에 `ema20_slope` 컬럼 누락 → 필터 무효화
- **수정**: `enrich_indicators()` 끝에 `df["ema20_slope"] = df["ema20"].diff() / df["ema20"]` 추가
- **재실험 결과** (ema_slope_min_buy=0.001, ema_slope_max_sell=-0.001):
  - 개선: fold3 -10.794→-8.828, fold1 -3.828→-2.852
  - 악화: fold2 1.540→-1.763, 저거래 fold 60%로 증가
  - 결론: threshold 너무 엄격 → `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]` 기본값(0.0) 복원

### F(리서치): 1h FAIL 근본 원인 + slippage regime 활용 분석
- 1h paper_sim의 주요 실패 원인: **PF < 1.5** (profit_factor 관련 failures가 ~70%)
- BTC 1h는 trend signal 대비 noise 비율이 높아 win/loss ratio 불리
- 4h에서 cmf/supertrend PASS → 타임프레임 자체가 핵심 차별화 요인
- Train window 축소 실험(TRAIN_HOURS=2016h) → 다음 사이클 C(데이터)에서 검토

## 시뮬레이션 결과 요약

| 항목 | 결과 |
|------|------|
| 테스트 | 8400 passed, 23 skipped |
| Paper Sim 1h PASS | 0/22 |
| Paper Sim rank1 | price_cluster (score=75.7, 3/8 consistent) |
| Bundle OOS PASS | 2/5 (cmf=2.508, supertrend=3.674) |
| narrow_range ema_slope | 부분 개선 but 저거래 악화 → 기본값 복원 |

## 다음 사이클 (312) 방향
- B(리스크): KellySizer kelly_reduce_at_mdd 파라미터 검토, CircuitBreaker 활용 검토
- D(ML): narrow_range nr_lookback=3 실험 (저거래 문제 해결)
- F(리서치): TRAIN_HOURS=2016h 실험 설계
