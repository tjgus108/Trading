# Current Cycle Briefing

_Last updated: 2026-07-07 (Cycle 401 완료)_

## 현재 상태

- **완료된 사이클**: 401
- **다음 사이클**: 402 (402 mod 5 = 2 → C+E+F)
- **1h paper_sim PASS**: 1/19 (ETH+SOL 합산 0/19 PASS — engulfing_zone 상대적 1위, frama 0/8)
- **frama 1h 탐색 완전 종료**: 8.1 trades/OOS window < min_trades=15 → 구조적 PASS 불가
- **Bundle OOS**: 5/5 PASS (2026-07-04 기준, SSL 차단으로 신규 실데이터 불가)
- **전체 테스트 수**: 8580개 (+12 from Cycle 401)

## Cycle 401 주요 결과

### B(리스크): DrawdownMonitor sharpe_decay + KellySizer regime 엣지케이스 (6개 추가)

- `tests/test_drawdown_monitor.py`:
  - `test_sharpe_decay_negative_recent_sharpe_triggers_decay`: negative recent_sharpe → 0.5x 적용
  - `test_sharpe_decay_recovery_after_decayed_state`: decay 이후 good sharpe → 1.0 복원
  - `test_atr_elevated_and_sharpe_decay_combined_size_multiplier`: ATR+Sharpe 동시 decay → 0.5x min
- `tests/test_kelly_sizer_regime_edge_cases.py`:
  - `test_large_n_above_min_trades_no_shrinkage`: n≥min_trades → Bayesian shrinkage 없음
  - `test_capital_scales_position_size`: capital 2배 → size 2배 선형 비례
  - `test_ranging_regime_reduces_size_vs_no_regime`: RANGING regime → default보다 작은 사이즈

### D(ML): frama WFO grid 테스트 (6개 추가)

- `tests/test_phase_d.py` — `TestFramaWfoGrid` 클래스:
  - `test_default_grids_frama_has_weak_rsi_buy_max`: DEFAULT_GRIDS["frama"]에 weak_rsi_buy_max 존재
  - `test_frama_grid_produces_27_combinations`: 3×3×3 = 27 combos 검증
  - `test_frama_strategy_stores_weak_rsi_buy_max`: 파라미터 저장 검증
  - `test_frama_strategy_default_weak_rsi_buy_max_is_40`: 기본값 40 검증
  - `test_optimize_frama_factory_passes_weak_rsi_buy_max`: WFO가 weak_rsi_buy_max 전달 확인
  - `test_frama_different_instances_independent_params`: 인스턴스 간 파라미터 독립성

### F(리서치): frama 1h 탐색 종료 결론

- **근본 원인 분석 완료**: frama 65 trades / 8 OOS windows = 8.1 trades/window < min_trades=15
- weak_rsi_buy_max=60 해도 ~100 trades → 12.5/window — PASS 불가 (구조적 한계)
- **결정**: frama 1h 탐색 영구 종료. WFO 그리드는 유지 (자동화), 수동 실험 중단.

## 다음 사이클 (402): C+E+F

- **C(데이터)**: DataFeed 또는 피처 엔지니어링 미커버 케이스
- **E(실행)**: OrderExecutor 또는 슬리피지 모델 테스트
- **F(리서치)**: engulfing_zone 성과 분석 — Sh=0.78(SOL), 0/8 Consistency 원인 파악
