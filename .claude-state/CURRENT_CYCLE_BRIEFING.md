# Current Cycle Briefing

_Cycle 306 완료 — 2026-06-13_

## 완료된 작업

### B(리스크) — DrawdownMonitor 재시작 복원 버그 수정
- `src/risk/drawdown_monitor.py`: `_tiered_halt`, `_halt_drawdown` 직렬화 추가
  - **버그**: 재시작 후 _tiered_halt=False로 초기화 → tiered recovery 로직이 legacy로 대체
  - **수정**: `to_dict()`에 두 필드 추가, `from_dict()`에서 `.get()` 복원
  - 기존 테스트 301개 PASS (backward compatible)

### D(ML) — narrow_range trend_regime_filter 실험 결과 분석
- `scripts/run_bundle_oos.py`: BUNDLE_STRATEGY_INIT_PARAMS에 narrow_range 추가
  - `trend_regime_filter=True, atr_trend_max=1.4`
  - **결과**: 효과 없음 — fold1=-3.828, fold3=-10.794 완전 동일
  - **원인**: BTC 4h 점진적 추세에서 ATR/ATR_MA(20) ratio가 1.4 미만
    - fold3 max=1.236 (0번 트리거), fold1 max=1.447 (2번만 트리거)
  - **다음**: atr_trend_max=1.1 실험 (Cycle 307)

### F(리서치) — cmf_1h period 상향
- `src/backtest/walk_forward.py`: cmf_1h period [60,75,90]→[75,90,105]
  - 4h CMF PASS (Sharpe=2.508) vs 1h CMF FAIL (Sharpe=-1.44) 원인 연구
  - 1h 노이즈 억제를 위해 더 긴 기간 탐색

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| Paper Sim BTC 1h | 0/22 PASS, rank1=price_cluster(75.7), rank2=supertrend_multi(68.3) |
| Bundle OOS BTC 4h | 2/5 PASS — cmf(2.508), supertrend_multi(3.674) |
| 테스트 | 8394 passed, 23 skipped |

## 다음 사이클 (307, 307 mod 5 = 2 → B + D + F)
1. B(리스크): DrawdownMonitor to_dict/from_dict tiered halt roundtrip 테스트 추가
2. D(ML): narrow_range atr_trend_max=1.1 Bundle OOS 실험
3. F(리서치): cmf_1h period=105 paper sim 결과 분석
