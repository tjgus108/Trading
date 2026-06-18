# Next Steps

_Last updated: 2026-06-18 (Cycle 328 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 328

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 326 | B+D+F | vol_multiplier 1.5→2.0, roc_ma_cross WFO 그리드 추가 |
| 327 | B+D+F | adx_threshold 25→22, roc_ma_cross WFO 실행(ma_period=7 역효과 확인→되돌림) |
| 328 | C+B+F | adx_threshold 효과 검증, regime_filter 옵션 추가, roc_ma_cross 필터 분석 |

### 🎯 Cycle 329 작업 방향 (329 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): roc_ma_cross RSI 필터 제거 + ROC_MIN_ABS 하향

- **배경**: Cycle 328 F(리서치) 분석 결과
  - RSI<70 차단: 0% (완전 무의미)
  - 모든 필터 제거해도 8.4 signals/window (목표 30+/window 미달)
  - **근본 원인**: ROC_MIN_ABS=0.3% 기준이 1h에서 너무 높음
- **실험**: `roc_ma_cross.py`에서 RSI 필터 제거 + ROC_MIN_ABS 0.3%→0.1% 하향
  - **단, 한 번에 하나씩 변경** — 먼저 RSI 제거만, 다음 ROC_MIN_ABS 조정
  - 목표: paper sim에서 40+ signals/window → WFO 통계적 신뢰도 확보
- **주의**: 필터 완화는 오신호 증가 위험 → PF 1.5+ 유지 여부 반드시 확인

#### E(실행): regime_filter=True positional_scaling WFO 실험

- **배경**: Cycle 328 B(리스크)에서 `WalkForwardOptimizer(regime_filter=True)` 구현 완료
- **실험**: positional_scaling WFO를 regime_filter=True로 실행
  - `DEFAULT_GRIDS`에 `positional_scaling` 그리드가 없으면 기본 파라미터로 실행
  - OOS fold별 TREND_UP 구간만 BUY → 1/8 → 2/8+ PASS 여부 확인
  - **성공 시**: paper_simulation.py STRATEGY_REGIME_FILTER 설정 추가 검토
- **검증**: 레짐 필터 적용 전후 1h paper sim 비교

#### F(리서치): roc_ma_cross 1h vs 4h 성과 비교 분석

- **배경**: 1h (8.4 signals/window) vs 4h (목표 30+ 가능성)
  - roc_ma_cross는 4h 타임프레임에서 ROC_MIN_ABS=0.3%가 의미있는 필터
  - 4h 이동 시 bundle OOS 전략 6개로 증가 (현재 5개)
- **분석**: 합성 데이터가 아닌 코드 분석으로 4h 신호 빈도 추정
  - `roc_ma_cross` 기본 파라미터(roc_period=12, ma_period=3) 4h CSV 실험
  - 1h 처럼 EMA/RSI 모두 확인 후 판단

### ⚠️ 주의 사항 (Cycle 329)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 328)
- 테스트: **104 passed** (regime+walk_forward 대상), 전체는 baseline 8413
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (변화 없음)
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (return=+1.97%, Sharpe=0.00, 1/8)
  - rank3: roc_ma_cross (return=+0.38%, Sharpe=-0.35, 2/8)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (8사이클 연속!)
  - order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - value_area: PASS (avg=3.069, std=0.085, rank3) ← std 최저!
  - vwap_cross: PASS (avg=3.047, std=1.437, rank4)
  - cmf: PASS (avg=2.508, std=1.888, rank5)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### Cycle 328 코드 변경 요약
- `src/strategy/regime.py`: `MarketRegimeDetector.detect_series()` 추가 (B리스크)
  - 전체 DataFrame 벡터화 레짐 계산 (O(n), detect_history O(n²) 대비 효율)
  - iloc[-2] 기준으로 미래 데이터 누출 방지
- `src/backtest/walk_forward.py`: `regime_filter` 옵션 추가 (B리스크)
  - `_RegimeFilterStrategy` 내부 클래스 (TREND_UP 아닌 봉 BUY 차단)
  - `WalkForwardOptimizer(regime_filter=True)` IS+OOS 모두 레짐 필터 적용

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 328 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 328 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 328 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
