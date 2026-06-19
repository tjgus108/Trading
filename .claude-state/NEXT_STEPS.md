# Next Steps

_Last updated: 2026-06-19 (Cycle 330 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 330

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 328 | C+B+F | adx_threshold 효과 검증, regime_filter 옵션 추가, roc_ma_cross 필터 분석 |
| 329 | D+E+F | roc_ma_cross RSI 필터 제거, detect_series() enum 버그 수정, positional_scaling regime_filter 비교 |
| 330 | A+C+F | ROC_MIN_ABS 0.1% 실험→즉시 되돌림(Sharpe악화), regime_filter 테스트 3개 추가, 수수료 근본원인 확인 |

### 🎯 Cycle 331 작업 방향 (331 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): 1h 고빈도 전략 수수료 burden 감소 — 신호 선택성 강화

- **배경**: Cycle 330 F(리서치) 결론 — 수수료가 Paper Sim 0/20 PASS 주범
  - 대부분 전략의 gross return (수수료 전) ≈ +8~14% → 수수료 8.82~16.38% 상쇄
  - **목표**: 1h 전략 거래수 절반 목표 (현재 40~80/window → 20~40/window)
  - price_cluster (45→22 trades): fee burden 9.45%→4.7% → net return 개선 예상
- **구체 실험**: BacktestEngine `min_profit_pct` 또는 포지션 최소 유지 봉수 추가
  - 현재 `engine.py`에 최소 보유 봉수(min_hold_bars) 파라미터 확인
  - 없으면: `risk/` 모듈에 min_hold_bars 옵션 추가 (1h에서 4봉=4h 최소 보유)
  - 또는: `walk_forward.py` 그리드에 `min_hold_bars: [4, 8]` 추가

#### D(ML): price_cluster 신호 선택성 강화 파라미터 탐색

- **배경**: Cycle 330 Paper Sim rank1 price_cluster (return=+2.19%, 1/8, 45 trades)
  - 수수료 전 gross ≈ +11.64% → 신호 수 절반이면 +2%+4.7%비용 = 가능성 있음
  - `close_window=[50,60]` + `n_bins=[4,5,6]` + `bounce_pct=[0.020,0.025,0.030]`
- **실험**: WFO로 price_cluster 파라미터 최적화 (regime_filter=True 포함)
  - 목표: 거래수 20~25/window, PF≥1.5, Sharpe≥1.0 (현재 0.34)
  - `vol_atr_trend_min` 상향 [1.5,2.0,2.5] 탐색 → 강한 추세에만 진입

#### F(리서치): 1h 수수료 0 시뮬레이션 실행 (정량화)

- **배경**: Cycle 330에서 수수료 impact 추정 완료 (gross return ≈ +8~14%)
  - 추정의 한계: fee_rate=0 실제 시뮬로 검증 필요
- **실험**: `paper_simulation.py`에 `--fee-rate 0.0 --slippage 0.0` 인자 추가
  - 인자 추가 후 BTC 1h 시뮬 실행 → PASS 전략 수 확인
  - 결과 비교: 현재 0/20 vs 수수료 0 시뮬 X/20 → 수수료 효과 정량화
  - 분석: 어떤 전략이 가장 높은 gross alpha인지 순위화

### ⚠️ 주의 사항 (Cycle 331)
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3% 복원)
  - ROC_MIN_ABS 추가 하향 실험 금지 — 이미 0.1% 역효과 확인
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}`
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}`
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}`
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### ⚠️ 주의 사항 (Cycle 330)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v4 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 330)
- 테스트: **8416 passed, 23 skipped** (+3 신규, 회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (10사이클 연속)
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (return=+1.97%, Sharpe=0.00, 1/8)
  - rank4: roc_ma_cross (return=-1.02%, Sharpe=-0.74, 2/8) ← _ROC_MIN_ABS=0.1 실험 실패, 복원 완료
  - **수수료 분석**: gross return ≈ +8~14% (수수료 8~16% 상쇄가 주원인)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (10사이클 연속!)
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
