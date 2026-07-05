# Current Cycle Briefing

_Last updated: 2026-07-05 (Cycle 397 완료)_

## 현재 상태

- **완료된 사이클**: 397
- **다음 사이클**: 398 (398 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.24, PF=1.12, Trades=40 — rsi_weak_buy_max=55 DEAD PARAM 확정
- **Bundle OOS**: 5/5 PASS (4h BTC 실데이터)
- **전체 테스트 수**: 8532개 (+6)

## Cycle 397 주요 결과

### B(리스크): DrawdownMonitor 경계값/윈도우 엣지케이스 6개 추가

- `tests/test_drawdown_monitor.py`: 6개 테스트 추가 (총 129개)
  - `test_transition_cushion_enabled_exact_threshold`: confidence==threshold → 1.0 (경계값 ≥)
  - `test_transition_cushion_enabled_zero_confidence`: confidence=0 → 0.5 반환
  - `test_transition_cushion_enabled_full_confidence`: confidence=1.0 → 1.0 반환
  - `test_rolling_mdd_window_one_returns_zero`: window=1 → 요소 1개 → 0.0
  - `test_rolling_mdd_window_equals_history_length`: window==len(history) → 자르지 않음
  - `test_trailing_stop_signal_very_small_rolling_window`: rolling_window=4 → short_window=2 → False

### D(ML): frama rsi_weak_buy_max 파라미터 실험 — DEAD 확정

- `src/strategy/frama.py`: `rsi_weak_buy_max=40` 파라미터 추가 (하드코딩→가변화)
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["frama"]에 rsi_weak_buy_max=[40] 추가
- **실험 결과** (rsi_weak_buy_max=55 vs 40):
  - rsi_weak_buy_max=55: Sh=0.15(↓-0.09), PF=1.08(↓-0.04), Trades=71(↑+31), Consist=1/8
  - 원인: RSI 40~55 구간 weak 크로스는 노이즈 신호 → PF/Sharpe 하락
  - **결론**: rsi_weak_buy_max=40 확정 불변. 추가 완화 실험 금지.

### F(리서치): frama atr_contracting dead code 발견

- `src/strategy/frama.py`: `atr_contracting` 계산되나 신호 게이팅 조건에 미사용
  - `if crossed_up and rsi_buy_ok:` — `atr_contracting` 포함 안 됨
  - ATR 변동성 필터가 실질적으로 비활성화 상태 (dead code in condition)
- `src/backtest/walk_forward.py`: 주석으로 문서화

### 시뮬레이션 결과

- **Paper Sim (1h BTC)**: 1/19 PASS — roc_ma_cross (Sh=1.81, PF=2.02, Trades=14, Consist=4/8)
- **Bundle OOS (4h BTC 실데이터)**: 5/5 PASS
  - order_flow_imbalance_v2: Sh=4.345
  - supertrend_multi: Sh=3.892
  - value_area: Sh=3.069
  - vwap_cross: Sh=3.047
  - cmf: Sh=2.508
