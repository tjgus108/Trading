# Next Steps

_Last updated: 2026-06-19 (Cycle 332 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 332

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 330 | A+C+F | ROC_MIN_ABS 0.1% 실험→즉시 되돌림(Sharpe악화), regime_filter 테스트 3개 추가 |
| 331 | B+D+F | min_hold_bars 추가, price_cluster 그리드 업데이트, fee=0 gross alpha 실험 |
| 332 | B+D+F | paper_sim --min-hold-bars CLI 추가, OFI v2 trend_span=15 실험→역효과 확인 복원 |

### 🎯 Cycle 333 작업 방향 (333 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): WebSocket / DataFeed 안정성 점검

- **배경**: SSL 차단 환경에서 CSV fallback이 핵심 — WebSocket/DataFeed 코드 유효성 확인
- **작업**: `src/data/` 모듈 점검
  - `data_utils.py` load_csv_ohlcv() / resample_ohlcv() 엣지케이스 테스트 확인
  - `tests/test_data_utils.py` 커버리지 확인 (누락 경로 보완)
  - ETH/USDT 합성 CSV vs BTC 실데이터 구분 로직 확인 (paper_sim load_ohlcv_from_csv_dir)

#### B(리스크): min_hold_bars 실제 효과 측정 — --min-hold-bars 4 실험

- **배경**: Cycle 332 --min-hold-bars CLI 추가 완료 (BacktestEngine 연결 검증됨)
  - 다음 단계: 실제 효과 측정 (min_hold_bars=4 vs 0 Sharpe 비교)
- **실험**: `python3 scripts/paper_simulation.py --csv-dir data/historical --symbols BTC/USDT --min-hold-bars 4`
  - 거래수 변화 및 Sharpe/PF 변화 측정
  - price_cluster rank1이 4봉 대기로 개선되는지 확인

#### F(리서치): OFI v2 그리드 탐색 — trend_span=25 실험

- **배경**: Cycle 332 결과 — trend_span=15 역효과 확인 (avg=4.036, std=2.771 → FAIL)
  - trend_span=20 복원 완료. 다음 탐색: trend_span=25 (더 긴 추세 필터)
- **작업**: `run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS 변경
  - `{"trend_span": 25}` 실험 (80h→100h EMA)
  - 목표: avg_sharpe > 5.0, std < 0.8 (현재 4.345/0.907)
  - 역효과면 즉시 복원 (trend_span=20 유지 정책)

### ⚠️ 주의 사항 (Cycle 333)
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3% 복원)
  - ROC_MIN_ABS 추가 하향 실험 금지 — 이미 0.1% 역효과 확인
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}`
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}`
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}`
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` (Cycle 332 실험 후 복원)
  - trend_span=15 역효과 확인 → trend_span=25 다음 탐색
- **min_hold_bars**: BacktestEngine + paper_simulation CLI 완료 (Cycle 332). 실제 효과 측정 필요

### ⚠️ 주의 사항 (Cycle 331, 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 332)
- 테스트: **8419 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (12사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
  - OFI (trend_span=15) rank11 (Sharpe=-1.03) — 실험 중 임시 악화, 복원 완료
- Bundle OOS BTC 4h (5-fold, OFI 실험 파라미터): **4/5 PASS** (OFI v2 실험 FAIL)
  - order_flow_imbalance_v2: **FAIL** (avg=4.036, std=2.771, trend_span=15 실험)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank1)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - ⚠️ 파라미터 복원 완료 (trend_span=20) → 다음 사이클 5/5 복구 예정

### 핵심 메트릭 (Cycle 331, 이전)
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
