# Current Cycle Briefing

_Cycle 310 | 2026-06-14 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): cmf 1h period=40 실험 → 역효과 확인
- 가설: 1h CMF noise 취약성은 lookback이 짧아서 → period=40 실험
- 결과: Sharpe -1.21 → -2.33, trades 72 → 59 (rank14 → rank19)
- 결론: 1h CMF는 period 무관하게 구조적으로 약함. 4h bars가 intraday noise 필터링
- 조치: paper_sim cmf params → `{"buy_thresh": 0.10}` (period=20 복원)

### C(데이터): NarrowRangeStrategy EMA slope 필터 구현
- `src/data/feed.py`: `ema20_slope = ema20.diff() / ema20` 지표 추가
- `src/strategy/narrow_range.py`: `ema_slope_min_buy`, `ema_slope_max_sell` 파라미터 추가
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["narrow_range"] 그리드 업데이트
- `scripts/run_bundle_oos.py`: narrow_range init params 업데이트
  - 기존: `trend_regime_filter=True, atr_trend_max=1.1` (효과 없음 확정)
  - 신규: `trend_regime_filter=False, ema_slope_min_buy=0.001, ema_slope_max_sell=-0.001`
  - 목표: fold3 OOS=-10.794 (BTC 불마켓 SELL 차단) 개선

### F(리서치): 슬리피지 레짐 추적 분석
- slippage_regime_counts 구현됨 (Cycle 309)이지만 리포트에 미반영
- 다음 사이클 B(리스크) 태스크: paper_sim generate_report()에 slippage 레짐 컬럼 추가

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| Paper Sim 1h | 0/22 PASS (동일), price_cluster rank1, cmf rank19(period=40 역효과) |
| Bundle OOS 4h | 2/5 PASS (cmf, supertrend_multi), narrow_range fold3=-10.794 지속 |

## 다음 사이클 (311): B(리스크) + D(ML) + F(리서치)
1. B: paper_sim 리포트에 slippage_regime_counts 추가
2. D: Cycle 311 Bundle OOS에서 narrow_range ema_slope 효과 확인
3. F: 1h 전체 FAIL 근본 원인 탐구 (WF 윈도우 설정 검토)
