# Current Cycle Briefing

_Last updated: 2026-07-05 (Cycle 396 완료)_

## 현재 상태

- **완료된 사이클**: 396
- **다음 사이클**: 397 (397 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (Cycle395 실데이터 — 최신)
- **전체 테스트 수**: 8526개 (+6)

## Cycle 396 주요 결과

### B(리스크): DrawdownMonitor 미커버 케이스 6개 추가

- `tests/test_drawdown_monitor.py`: should_kill_strategy HIGH_VOL 레짐 테스트
  - HIGH_VOL cap=1.0 → threshold=0.10 (backtest MDD 초과 즉시 kill) 검증
- `tests/test_drawdown_monitor.py`: should_kill_strategy RANGING 레짐 테스트
  - RANGING cap=1.2 → threshold=0.12 (빠른 kill) 검증
- `tests/test_drawdown_monitor.py`: should_kill_strategy TREND_DOWN 레짐 테스트
  - TREND_DOWN cap=1.2 → threshold=0.12 검증
- `tests/test_drawdown_monitor.py`: should_kill_strategy 알 수 없는 레짐 fallback 테스트
  - 미정의 레짐 → multiplier 그대로 사용 검증
- `tests/test_drawdown_monitor.py`: get_size_multiplier MDD WARN + ATR elevated 조합 테스트
  - min(streak=1.0, mdd=0.5, atr=0.5, sharpe=1.0) = 0.5 검증
- `tests/test_drawdown_monitor.py`: get_size_multiplier MDD BLOCK + streak 조합 테스트
  - min(streak=0.5, mdd=0.0) = 0.0 (BLOCK 우선) 검증

### D(ML): dema_cross WFO 그리드 dead param 현행화

- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["dema_cross"] 각 파라미터에 dead param 주석 추가
  - fast=10,12 DEAD (8 확정), slow=15,25 DEAD (20 확정)
  - rsi_dir_filter=False DEAD, rsi_dir_threshold=45 DEAD
  - ema_slope_min_buy=0.0003 DEAD, macd_hist_filter=True DEAD
  - bb_width_min_filter=0.0 DEAD, ema200_filter=True DEAD
  - Cycle396 종료 선언 주석 + 확정 파라미터 문서화

### F(리서치): 시뮬 결과 분석 + 다음 방향 결정

- **Paper Sim BTC 1h**: roc_ma_cross PASS(4/8, Sh=1.81) 유지 / price_cluster Sh=1.06 2/8 / dema_cross Sh=0.85 PF=1.38
- **다음 최적화 대상**: **frama** (Sh=0.24, PF=1.12, Trades=40, +1.60% avg return)
  - 이유: Trades=40 풍부 (signal 부족 없음), positive return edge 존재
  - 미래: frama WFO 그리드 탐색 → atr_period 최적화 → Sharpe ≥ 1.0 목표
  - 이전 탐색: atr_period=[10,14,18] WFO 그리드 존재 (Cycle363 F 추가)
