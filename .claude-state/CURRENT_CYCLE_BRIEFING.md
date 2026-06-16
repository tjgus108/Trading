# Current Cycle Briefing

_Cycle 319 | 2026-06-16 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML) — price_cluster bounce_pct=0.025→0.015 실험

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"] 수정
- 결과: 저거래 비율 80%→60% 개선, avg Sharpe 3.672→3.823
- 하지만 std=3.854>>2.0 (fold2 OOS=1.098 FAIL로 불안정)
- 결론: 여전히 FAIL — fold2 WFE=0.000 (IS=-2.35 음수, OOS 양수 구간)

### E(실행) — live_paper_trader.py Bundle PASS 전략 우선순위 설정

- `BUNDLE_PASS_PRIORITY`: OFI v2 → supertrend_multi → cmf 순서
- `BUNDLE_PASS_WEIGHTS`: OFI v2(40%), supertrend_multi(35%), cmf(25%)
- `initialize()` fallback: Bundle PASS 먼저 선택
- position sizing: `bundle_weight_mult` 적용

### F(리서치) — value_area 분석 + 코드 개선

- value_area: max_oos_sharpe_std=2.5 완화 불충분 — fold0/3 음수 Sharpe
- `run_bundle_oos.py`: 합성 데이터 run이 실 데이터 리포트 덮어쓰기 방지 (`_using_real_data` 플래그)

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h**: 0/22 PASS (기존 유지)
- **Bundle OOS BTC 4h**: 3/5 PASS (OFI v2, supertrend_multi, cmf)
  - price_cluster: FAIL (bounce_pct=0.015, 저거래 60%, std=3.854)
  - value_area: FAIL (avg=0.713, std=2.018)

## 다음 사이클 (320, mod5=0 → A+C+F)

- **A**: IS 음수 fold WFE 계산 로직 검토 (walk_forward.py) — fold2 IS=-2.35, OOS=1.098 처리
- **C**: value_area BUNDLE_STRATEGY_OVERRIDES 추가 (regime_transition_is_min=2.0 + min_oos_trades=5)
- **F**: price_cluster/value_area 대안 전략 탐색 (기존 355+ 전략 중)
