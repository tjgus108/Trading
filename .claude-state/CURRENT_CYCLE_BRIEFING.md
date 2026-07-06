# Current Cycle Briefing

_Last updated: 2026-07-06 (Cycle 401 완료)_

## 현재 상태

- **완료된 사이클**: 401
- **다음 사이클**: 402 (402 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.44, Trades=65, 0/8 Consistency — **탐색 종료 확정** (구조적 한계)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (2026-07-06)
- **전체 테스트 수**: 8580개 (+12)

## Cycle 401 주요 결과

### B(리스크): DrawdownMonitor sharpe_decay 경계값 + regime cooldown 복합 (6개 추가)

- `tests/test_drawdown_monitor.py` (6개):
  - `test_sharpe_decay_negative_recent_sharpe_detects_decay`: OOS Sharpe 음수 → decay 0.5x
  - `test_sharpe_decay_recovery_after_decay_resets_to_1x`: decay 후 정상 회복 → 1.0x
  - `test_get_size_multiplier_atr_and_sharpe_decay_both_elevated`: ATR+decay 동시 → 0.5x
  - `test_ranging_neutral_macro_reduces_effective_cooldown`: RANGING+neutral → base×0.9
  - `test_ranging_directional_macro_extends_effective_cooldown`: RANGING+directional → base×1.5
  - `test_ranging_no_macro_info_uses_default_ranging_multiplier`: RANGING+None → base×1.2

### D(ML): optimize_frama WFO weak_rsi_buy_max 그리드 검증 (6개 추가)

- `tests/test_phase_d.py` TestOptimizeFramaWeakRsi 클래스 (6개):
  - `test_default_grid_has_three_weak_rsi_values`: DEFAULT_GRIDS["frama"]["weak_rsi_buy_max"]==[40,50,60]
  - `test_optimize_frama_best_params_contains_weak_rsi_key`: WFO best_params에 key 존재
  - `test_optimize_frama_best_params_weak_rsi_in_valid_range`: 값이 [40,50,60] 중 하나
  - `test_optimize_frama_factory_propagates_weak_rsi_50/60`: factory 전달 정확성
  - `test_optimize_frama_window_params_have_valid_weak_rsi`: window별 params 유효성

### F(리서치): frama 0/8 Consistency 구조적 한계 최종 확정

- 코드 레벨 분석: gap>=1%(강한신호) vs gap<1%(약한신호) 분기
- RANGING(47.3%): gap<1% 대부분 + RSI 중립(40-60) → 약한신호 경로 차단 구조
- weak_rsi_buy_max=[40,50,60] 탐색: Trades 증가하지만 Consistency 개선 불가
- **결론**: frama는 gap>=1% 추세추종 전략. RANGING 구간 구조적 불리. 파라미터로 해결 불가.
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["frama"] 주석에 Cycle401 F 최종 결론 추가
- WFO 그리드 [40,50,60] 유지 (자동 최적값 선택용), paper_sim weak_rsi=50 유지

## 다음 사이클 (402): B+D+F

- **B(리스크)**: KellySizer 미커버 케이스 (compute_from_trades 대용량/음수 PnL, get_dynamic_fraction 경계값)
- **D(ML)**: MLSignalGenerator 또는 walk_forward 추가 커버리지
- **F(리서치)**: dema_cross(PF 1.38→1.50 방향) 또는 price_cluster(Consistency 2/8 해소 가능성) 분석
