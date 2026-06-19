# Next Steps

_Last updated: 2026-06-19 (Cycle 329 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 329

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 327 | B+D+F | adx_threshold 25→22, roc_ma_cross WFO 실행(ma_period=7 역효과→되돌림) |
| 328 | C+B+F | adx_threshold 효과 검증, regime_filter 옵션 추가, roc_ma_cross 필터 분석 |
| 329 | D+E+F | roc_ma_cross RSI 필터 제거, detect_series() enum 버그 수정, positional_scaling regime_filter 비교 |

### 🎯 Cycle 330 작업 방향 (330 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): roc_ma_cross ROC_MIN_ABS 0.3%→0.1% 하향 실험

- **배경**: Cycle 329 D(ML)에서 RSI 필터 제거 후에도 Sharpe=-0.41 (미세 악화)
  - 1h: cross_above=57/window → EMA50 통과=35.5/window (EMA가 주 차단 요인)
  - F(리서치): 1h 신호 빈도 35.5/window ← 4h(14.6/fold)보다 많음
  - **진짜 병목**: ROC_MIN_ABS=0.3% (57→50.5 = 11.4% 차단)보다 EMA50이 더 큰 차단
  - ROC_MIN_ABS 0.1%로 내리면 50.5 → 57 (6.5개 추가) = 기대효과 제한적
- **실험 방법**: `_ROC_MIN_ABS = 0.1`로 변경 후 paper_sim 실행
  - 목표: 2/8 → 3/8+ consistency (PF 1.5+ 유지 확인 필수)
  - **실패 판단**: PF<1.2이면 즉시 되돌림
- **주의**: 오신호 증가 위험 — 반드시 paper_sim 검증 후 판단

#### C(데이터): detect_series() 버그 수정 후 regime_filter=True WFO 실제 실행 검증

- **배경**: Cycle 329에서 pandas 3.x enum 비교 버그 수정 (dtype=object 추가)
  - Cycle 328에 추가된 regime_filter=True 기능이 실질적으로 ALL BUY 차단했음
  - 수정 후: positional_scaling 비교에서 TREND_UP=31.3% (정상)
- **실험**: WalkForwardOptimizer(regime_filter=True) 실제 동작 검증
  - test_walk_forward.py에 regime_filter=True 전용 테스트 추가 (컬럼 검증)
  - `_annotate_regime()` 결과가 30%+ TREND_UP 반환하는지 확인
  - 기존 104개 regime_filter 테스트가 enum 비교 오류로 잘못된 결과였는지 재확인

#### F(리서치): Paper Sim 0/20 근본 원인 분석

- **배경**: 9사이클 연속 0/20 PASS — 왜 1h paper sim이 계속 실패하는가?
  - rank1 price_cluster: 1/8 PASS (W3 2023 Q4 불마켓만)
  - rank2 positional_scaling: 1/8 PASS (동일 윈도우)
  - **공통 패턴**: 모두 W3(2023 Oct-Dec 불마켓)에서만 PASS
  - **가설 A**: BTC 1h 2023 데이터가 대부분 횡보/하락 → 장기 추세 전략 불리
  - **가설 B**: 수수료(0.055%/leg) + 슬리피지(0.05%) = 0.21% 왕복이 Sharpe를 압도
  - **분석**: 수수료 0으로 설정 후 시뮬 실행 → 수수료 효과 정량화
  - 분석 결과를 Cycle 331 작업 방향에 반영

### ⚠️ 주의 사항 (Cycle 330)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v4 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 329)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (변화 없음)
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (return=+1.97%, Sharpe=0.00, 1/8)
  - rank3: roc_ma_cross (return=+0.09%, Sharpe=-0.41, 2/8) ← RSI 제거 후 미세 악화
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (9사이클 연속!)
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

### Cycle 329 코드 변경 요약
- `src/strategy/roc_ma_cross.py`: RSI 필터 제거 (D(ML))
  - BUY: `rsi_val < 70` 조건 제거
  - SELL: `rsi_val > 30` 조건 제거
  - 버전 v3 → v4 (docstring 업데이트)
- `src/strategy/regime.py`: `detect_series()` pandas 3.x 버그 수정 (E(실행) 발견)
  - `pd.Series(regimes, index=df.index, dtype=object)` — dtype=object 명시
  - 기존: StringDtype 추론 → 벡터화 `== MarketRegime.TREND_UP` 항상 False
  - 영향: regime_filter=True 기능이 Cycle 328 이후 ALL BUY 차단하던 심각한 버그 수정

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 329 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 329 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 329 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
