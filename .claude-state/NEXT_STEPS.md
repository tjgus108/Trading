# Next Steps

_Last updated: 2026-06-19 (Cycle 331 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 331

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 329 | D+E+F | roc_ma_cross RSI 필터 제거, detect_series() enum 버그 수정 |
| 330 | A+C+F | ROC_MIN_ABS 0.1% 실험→즉시 되돌림(Sharpe악화), regime_filter 테스트 3개 추가 |
| 331 | B+D+F | min_hold_bars 추가, price_cluster 그리드 업데이트, fee=0 gross alpha 실험 |

### 🎯 Cycle 332 작업 방향 (332 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): min_hold_bars 실험 — 1h 전략 재진입 대기로 거래수 감소

- **배경**: Cycle 331 gross alpha 실험 결론 — 1h 전략 gross Sharpe ≈ 0.82 최대 (기준 1.0 미달)
  - 수수료 제거 후에도 0/20 PASS → 수수료만의 문제가 아닌 gross alpha 부족
  - **실질 전략**: 1h 개선보다 4h 강화가 현실적
- **실험**: paper_simulation에 `--min-hold-bars 4` 옵션 추가 및 WFO 실험
  - BacktestEngine에 `min_hold_bars` 파라미터 이미 추가됨 (Cycle 331)
  - `paper_simulation.py`에 `--min-hold-bars` CLI 인자 추가
  - BTC 1h 시뮬: min_hold_bars=0 vs 4 vs 8 비교 → 거래수 및 Sharpe 변화 측정

#### D(ML): 4h 전략 강화 — order_flow_imbalance_v2 그리드 탐색

- **배경**: Cycle 331 Bundle OOS rank1 order_flow_imbalance_v2 (avg_sharpe=4.345, std=0.907)
  - 이미 5/5 PASS + 최고 안정성 → 파라미터 최적화로 추가 개선 여지
  - `trend_span=20` 고정 → `[15, 20, 25]` 탐색
  - `delta_window` (현재 기본값) → `[5, 7, 10]` 탐색
- **목표**: avg_sharpe > 5.0, std < 0.8 (현재 4.345/0.907)

#### F(리서치): 4h 전략 전환 검토 — 1h 10연속 FAIL 결론 문서화

- **배경**: 1h gross alpha 실험 (Cycle 331) 결론:
  - fee=0에서도 0/20 PASS (gross Sharpe 최대 0.82 < 1.0 기준)
  - 4h는 11사이클 연속 5/5 PASS 유지
- **작업**: 1h 전략 개선 일시 중단 판단 문서화
  - `paper_simulation.py` 심볼에서 ETH/SOL 제거 옵션 검토 (BTC만 집중)
  - 4h 심볼 확장: ETH/USDT 4h CSV 존재 여부 확인
  - 결론을 NEXT_STEPS에 정책으로 기록

### ⚠️ 주의 사항 (Cycle 332)
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3% 복원)
  - ROC_MIN_ABS 추가 하향 실험 금지 — 이미 0.1% 역효과 확인
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}`
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}`
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}`
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **min_hold_bars**: BacktestEngine에 추가 완료 (Cycle 331). paper_simulation --min-hold-bars CLI도 추가 필요

### ⚠️ 주의 사항 (Cycle 331, 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 331)
- 테스트: **8419 passed, 23 skipped** (+3 신규 min_hold_bars, 회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (11사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, 0/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
  - **fee=0 gross**: price_cluster=0.82, positional_scaling=0.40 (기준 1.0 미달 확인)
  - **결론**: 수수료 제거 후에도 FAIL → 1h gross alpha 부족이 근본 원인
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (11사이클 연속!)
  - order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - vwap_cross: PASS (avg=3.047, std=1.437, rank4)
  - cmf: PASS (avg=2.508, std=1.888, rank5)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### Cycle 330 코드 변경 요약
- `src/strategy/roc_ma_cross.py`: v5 docstring 업데이트 (A(품질))
  - _ROC_MIN_ABS=0.1 실험 후 즉시 되돌림 (Sharpe -0.41→-0.74 악화 확인)
  - 버전 v4 → v5 (docstring: 실험 결과 및 결론 기록)
  - 최종 값: `_ROC_MIN_ABS = 0.3` (복원)
- `tests/test_walk_forward.py`: regime_filter=True 전용 테스트 3개 추가 (C(데이터))
  - `test_detect_series_returns_trend_up_on_uptrend()`: dtype=object + 30%+ TREND_UP 검증
  - `test_annotate_regime_adds_column()`: _regime_trend_up 컬럼 및 원본 불변 검증
  - `test_regime_filter_true_blocks_buy_on_ranging()`: RANGING BUY 차단 + TREND_UP 통과 검증

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 329 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 330 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
