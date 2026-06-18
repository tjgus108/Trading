# Next Steps

_Last updated: 2026-06-18 (Cycle 327 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 327

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 325 | A+C+F | value_area/supertrend_multi 1h 제외 확정, CSV 4h fallback 추가 |
| 326 | B+D+F | vol_multiplier 1.5→2.0, roc_ma_cross WFO 그리드 추가 |
| 327 | B+D+F | adx_threshold 25→22, roc_ma_cross WFO 실행(ma_period=7 역효과 확인→되돌림) |

### 🎯 Cycle 328 작업 방향 (328 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): adx_threshold=22.0 효과 검증

- **배경**: Cycle 327에서 adx_threshold 25→22로 완화 (TREND 감지 빈도 향상)
- **검증 과제**: 실제 BTC 1h CSV에서 TREND_UP 판정 비율 변화 측정
  - `MarketRegimeDetector(adx_threshold=25.0)` vs `(adx_threshold=22.0)` 비교
  - `detect_history(df_btc_1h, lookback=200)` → TREND_UP/DOWN/RANGING/HIGH_VOL 분포
  - 기대: TREND_UP 판정 빈도 15%+ 증가 시 확정
- **목표**: fold0(+132% bull 구간) HIGH_VOL → TREND_UP 재판정 확인

#### B(리스크): positional_scaling 레짐 필터 실험

- **배경**: positional_scaling 1/8 PASS — 레짐 필터 없이 횡보/하락 진입이 근본 원인
- **실험**: positional_scaling에 MarketRegimeDetector TREND_UP 조건 추가
  - **단, positional_scaling.py 직접 수정 금지** — 전략 코드는 변경하지 말 것
  - 대신: paper_simulation.py `STRATEGIES_TIMEFRAME_EXCLUDE` 또는 `regime_filter` 래퍼 방식 검토
  - `walk_forward.py`에 레짐 필터 옵션 추가가 더 안전
- **목표**: BUY 조건에 레짐 필터 적용 후 1/8 → 2/8+ PASS 여부

#### F(리서치): roc_ma_cross EMA/RSI 필터 완화 방향 분석

- **배경**: Cycle 327 WFO 결과 — 33 trades/8 windows (4.1/window), 통계적 신뢰도 부족
  - EMA50 cross filter + RSI<70 + ROC abs>0.3% 이중 필터가 1h 신호를 과도 차단
  - WFO best (ma_period=7)도 paper sim에서 rank2→rank6으로 악화
- **탐색 방향**: 어떤 필터가 가장 많은 신호를 차단하는지 분석
  - `roc_ma_cross.py`: EMA50 필터 제거 시 trades 수 변화 측정 (코드 변경 없이 분석만)
  - 조건 단순화: ROC_MA 크로스 + ROC abs>0.3% 만으로 trades 수 → 30+/window 가능?
  - 결과 기반으로 Cycle 329 D(ML) 계획 수립

### ⚠️ 주의 사항 (Cycle 328)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 327)
- 테스트: **8409 passed, 17 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략** — value_area/supertrend_multi 제외): **0/20 PASS**
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (return=+1.97%, Sharpe=0.00, 1/8)
  - rank6: roc_ma_cross (return=-1.10%, Sharpe=-0.69, 1/8) ← ma_period=7 역효과 확인
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (7사이클 연속)
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
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요 (ma_period=7 실험 시 더 길어짐)

### Cycle 327 코드 변경 요약
- `src/strategy/regime.py`: `adx_threshold` 기본값 25.0→22.0 (B리스크)
  - TREND_UP/DOWN 감지 ADX 임계값 완화 → 민감도 향상
  - 도큐스트링 ADX > 25 → ADX > 22 업데이트
- **되돌린 변경**: `scripts/paper_simulation.py` roc_ma_cross params 추가→제거
  - ma_period=7 paper sim rank6 (이전 rank2) → 역효과 확인, 즉시 복원

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 327 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 327 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 327 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
