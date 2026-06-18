# Next Steps

_Last updated: 2026-06-18 (Cycle 326 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 326

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 324 | D+E+F | supertrend_multi_1h 그리드 추가, live_paper_trader 4h 지원 |
| 325 | A+C+F | value_area/supertrend_multi 1h 제외 확정, CSV 4h fallback 추가 |
| 326 | B+D+F | vol_multiplier 1.5→2.0, roc_ma_cross WFO 그리드 추가 |

### 🎯 Cycle 327 작업 방향 (327 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): adx_threshold 완화 실험

- **배경**: vol_multiplier 2.0으로 HIGH_VOL 과다 판정 해소 (Cycle 326)
  - 다음 단계: ADX 기반 TREND 감지 민감도 향상 검토
  - 현재: `adx_threshold=25.0` (Wilder 기준) → 22.0 완화 시 TREND 감지 빈도 증가
- **실험**: `MarketRegimeDetector(adx_threshold=22.0)` vs `(25.0)` 비교
  - 테스트 데이터: BTC 1h CSV `_make_df(200, "up")` → TREND_UP 판정 비율 비교
  - 결과가 TREND_UP 더 자주 → 22.0 적용 확정 (과민 시 23.0으로 절충)
- **목표**: fold0(+132% bull 구간) → HIGH_VOL → TREND_UP 재판정 확인

#### D(ML): roc_ma_cross WFO 실행 (Cycle 326 그리드 활용)

- **현재 상황**: rank2 (2/8 consistency, return=+0.38%), FAIL 원인: Sharpe=-0.35, PF=1.12
  - Cycle 326에서 `roc_period=[10,12,15]`, `ma_period=[3,5,7]` 그리드 추가 완료
- **탐색 방향**: `optimize_roc_ma_cross(df_1h)` 실행
  - `data/historical/binance/BTCUSDT/1h.csv` 로드 → `optimize_roc_ma_cross` 실행
  - 최적 파라미터로 Paper Sim PAPER_SIM_STRATEGY_PARAMS 업데이트
- **평가 기준**: OOS Sharpe 개선 여부 (현재 avg=-0.35 → 목표 > 0.0)
- **단, 합성 데이터 사용 금지**: BTC 1h CSV로만 검증

#### F(리서치): positional_scaling 1/8 PASS 분석

- **현재 상황**: rank3 (return=+1.97%, Sharpe=0.00, 1/8 consistency)
  - 유일 PASS 윈도우 분석: 어떤 구간인지 확인 (bull/bear/ranging?)
  - PASS 조건: Sharpe≥1.0, PF≥1.5, Trades≥15, MDD≤20%
- **탐색 방향**: positional_scaling 전략 파라미터 현황 확인
  - `src/strategy/positional_scaling.py` 현재 로직 분석
  - 1/8 PASS 구간 특성이 bull 레짐이면 → roc_ma_cross와 레짐 매핑 비교

### ⚠️ 주의 사항 (Cycle 327)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 326)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략** — value_area/supertrend_multi 제외): **0/20 PASS**
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (return=+0.38%, 2/8 consistency — 최고!)
  - rank3: positional_scaling (return=+1.97%, PF=1.18, 1/8)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (6사이클 연속)
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
- Paper simulation 1h: **20 전략** × 8 windows → 약 7분 소요 (BTC 단독)

### Cycle 326 추가 코드 변경 요약
- `src/strategy/regime.py`: `vol_multiplier` 기본값 1.5→2.0 (B리스크)
  - HIGH_VOL 판정 강화: 현재 ATR이 20-bar 평균의 2배 초과 시에만
- `src/strategy/roc_ma_cross.py`: `roc_period`, `ma_period` 생성자 파라미터 추가 (D ML)
  - 기본값 유지 (roc_period=12, ma_period=3), `_min_rows` 동적 계산
- `src/backtest/walk_forward.py`: `DEFAULT_GRIDS["roc_ma_cross"]` + `optimize_roc_ma_cross()` 추가 (D ML)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 326 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 326 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 326 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
