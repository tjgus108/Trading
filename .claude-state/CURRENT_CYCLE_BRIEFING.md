# Current Cycle Briefing

_Cycle 331 | 2026-06-19 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): BacktestEngine min_hold_bars 파라미터 추가

- `src/backtest/engine.py`:
  - `min_hold_bars: int = 0` 파라미터 추가
  - 청산 후 N봉 재진입 대기 (post-trade cooldown)
  - 구현: cooldown_remaining 카운터, 청산 시 min_hold_bars로 리셋, 매 봉 끝 감소
  - 신호 생성: `position is None and cooldown_remaining == 0` 조건
  - `_build_engine()` valid_keys에 추가
- `tests/test_backtest_engine.py` 3개 테스트 추가:
  - `test_min_hold_bars_default_zero_no_effect()`: 기본값 동작 보존 확인
  - `test_min_hold_bars_reduces_trade_count()`: cooldown=8봉 거래수 감소 확인
  - `test_min_hold_bars_stored_in_engine()`: 파라미터 저장 확인

### D(ML): price_cluster 그리드 vol_atr_trend_min 업데이트

- `src/backtest/walk_forward.py` DEFAULT_GRIDS["price_cluster"]:
  - `vol_atr_trend_min: [1.3, 1.5, 2.0]` → `[1.5, 2.0, 2.5]`
  - 1.3 제거 (Cycle301 역효과 확인), 2.5 추가 (강한 추세 억제 탐색)

### F(리서치): --fee-rate/--slippage 인자 + gross alpha 실험

- `scripts/paper_simulation.py`:
  - `--fee-rate` / `--slippage` CLI 인자 추가
  - `run_simulation(fee_rate_override, slippage_override)` 파라미터 추가
  - metadata JSON에 실제 적용된 fee_rate/slippage 기록
- BTC/USDT 1h fee=0.0 slippage=0.0 시뮬레이션:
  - **결과: 0/20 PASS** (수수료=0에서도 전멸!)
  - best gross Sharpe: price_cluster=0.82, positional_scaling=0.40
  - **핵심 발견**: 수수료 제거 후에도 FAIL → 1h gross alpha 부족이 근본 원인
  - Cycle330 가설 수정: 수수료만의 문제가 아님 — gross Sharpe 최대 0.82 < 기준 1.0

## 시뮬레이션 결과

- **테스트**: 8419 passed, 23 skipped (+3 신규 min_hold_bars, 회귀 없음)
- **Paper Sim BTC 1h**: 0/20 PASS (11사이클 연속 전멸)
  - rank1: price_cluster (Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, 0/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
  - fee=0: price_cluster gross=0.82, positional_scaling gross=0.40
- **Bundle OOS BTC 4h**: 5/5 PASS (11사이클 연속!)
  - rank1: order_flow_imbalance_v2 (avg OOS Sharpe=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085) ← std 최저 안정
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (332 mod 5 = 2): B(리스크) + D(ML) + F(리서치)

- **B(리스크)**: paper_simulation에 --min-hold-bars CLI 인자 추가 후 min_hold_bars=4/8 효과 측정
- **D(ML)**: order_flow_imbalance_v2 4h WFO 그리드 탐색 (trend_span, delta_window)
- **F(리서치)**: 1h 전략 개선 일시 중단 판단 문서화 + 4h 심볼 확장 검토
