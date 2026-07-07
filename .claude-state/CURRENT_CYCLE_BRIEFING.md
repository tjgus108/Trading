# Current Cycle Briefing

_Last updated: 2026-07-07 (Cycle 401 완료)_

## 현재 상태

- **완료된 사이클**: 401
- **다음 사이클**: 402 (402 mod 5 = 2 → E+A+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44, Trades=65, 0/8 Consistency — 탐색 완전 종료 (RANGING 구조적 한계)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (2026-07-07, 실 BTC CSV 4h 재샘플링)
- **전체 테스트 수**: 8577개 (+9)

## Cycle 401 주요 결과

### B(리스크): DrawdownMonitor set_sharpe_decay 복합 조합 (6개 추가)

- `tests/test_drawdown_monitor.py`:
  - `test_sharpe_decay_and_atr_elevated_compound`: ATR elevated + Sharpe decay → min() 결합 검증
  - `test_sharpe_decay_negative_recent_sharpe_is_decayed`: 음수 recent_sharpe → decay 발동
  - `test_sharpe_decay_recovery_resets_multiplier`: 회복 후 multiplier=1.0 복원 확인
  - `test_sharpe_decay_zero_recent_sharpe`: recent_sharpe=0.0 → decay 발동
  - `test_sharpe_decay_custom_threshold_boundary`: ratio==threshold → < 조건 불성립 → 1.0
  - `test_sharpe_decay_and_mdd_warn_compound`: MDD WARN + Sharpe decay 복합 → 0.5

### D(ML): optimize_frama 파라미터 검증 (3개 추가)

- `tests/test_phase_d.py` (TestOptimizeFrama):
  - `test_optimize_frama_weak_rsi_key_in_best_params`: best_params에 weak_rsi_buy_max 포함
  - `test_optimize_frama_grid_combos_count`: DEFAULT_GRIDS["frama"] 27 combos (3×3×3)
  - `test_optimize_frama_no_atr_period_in_grid`: atr_period DEAD PARAM → 그리드 미포함

### F(리서치): frama 0/8 Consistency 근본 원인 코드 분석 완료

- frama.py 신호 구조: strong_signal(gap>=1%→RSI<85) vs weak_signal(gap<1%→RSI<weak_rsi_buy_max)
- RANGING(47.3% BTC 1h)에서 gap<1% 지배 → weak 신호 경로 주도, RSI 중립(40-60) 차단
- atr_contracting DEAD PARAM: BUY/SELL 조건 미사용, 로그 전용
- walk_forward.py에 Cycle401 F 분석 주석 추가
- **결론**: frama WFO 그리드 [40,50,60] 유지, frama 추가 탐색 종료

## 다음 사이클 (402): E+A+F

- **E(실행)**: PaperTrader / PaperConnector 미커버 케이스 (슬리피지 경계값, 잔고 부족 등)
- **A(품질)**: BacktestEngine / WalkForwardOptimizer 미커버 케이스 (fee 계산, 윈도우 분할 경계)
- **F(리서치)**: price_cluster / dema_cross / roc_ma_cross 개선 가능성 분석
