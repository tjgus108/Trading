# Next Steps

_Last updated: 2026-06-20 (Cycle 336 D(ML) 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 335

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 333 | C+B+F | data_utils 테스트+6, cooldown_suppressed 진단 필드, trend_span=25 실험→복원 |
| 334 | D+E+F | delta_window=5 실험→FAIL(avg=2.962,std=3.570), live_paper_trader CSV fallback 검증 |
| 335 | A+C+F | 청산이유 추적(sl/tp/max_hold), BTC CSV 갭 없음 확인, OFI imbalance_threshold 탐색 완료 |

### 🎯 Cycle 336 작업 방향 (336 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): MAX_HOLD_CANDLES 진단 기반 개선 탐색

- **배경**: Cycle 335 발견 — price_cluster 스모크테스트에서 14거래 중 max_hold=7 (50%)
  - SL=5, TP=2, MAX_HOLD=7 → TP 도달 전 강제청산이 PF 저하의 핵심 원인
  - 현재 MAX_HOLD_CANDLES=24 (1h 기준 24시간=1일)
- **작업**: BacktestEngine에서 1h 실데이터 기반 close_reason 분포 측정
  - price_cluster, roc_ma_cross, positional_scaling 대상으로 sl/tp/max_hold 비율 확인
  - MAX_HOLD_CANDLES=48 (2일) 실험: max_hold 강제청산 감소 → PF 개선 가능성 검토
  - **주의**: MAX_HOLD 증가 시 MDD 악화 위험 — 전략별 영향 측정 필수
- **금지**: price_cluster 전략 파일 수정 금지

#### D(ML): OFI v2 buy_thresh 1h 탐색

- **배경**: 1h Paper Sim에서 OFI rank10 (Sharpe=-0.83, PF=0.95)
  - 4h Bundle OOS에서는 rank1 (avg=4.345) — 타임프레임별 적합성 차이
  - buy_thresh=0.25는 1h에서 너무 많은 노이즈 신호 허용 가능성
- **작업**: PAPER_SIM_STRATEGY_PARAMS에 `order_flow_imbalance_v2: {"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` 실험
  - Paper Sim 1h에서 OFI 신호 빈도 측정 (현재 73거래/8윈도우 = 과다)
  - 0.30으로 강화 시 거래 감소 + PF 개선 가능성
  - **주의**: Bundle OOS 4h `BUNDLE_STRATEGY_INIT_PARAMS`는 변경 금지 (4h에서 이미 최적)

#### F(리서치): MAX_HOLD_CANDLES 영향 분석 + 논문 리서치

- **배경**: close_reason 추적 기능 추가로 진단 가능
- **작업**: BTC 1h 실데이터로 전략별 close_reason 분포 측정
  - 분포 측정 코드: engine.run() 후 result.sl_hits, tp_hits, max_hold_closes 로깅
  - MAX_HOLD_CANDLES 값 변화에 따른 PF/Sharpe 민감도 분석
- **리서치**: "Optimal holding period for crypto mean-reversion strategies" 관련 퀀트 논문

### ⚠️ 주의 사항 (Cycle 336)
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` (delta_window=10 기본값)
  - **Bundle OOS 파라미터 변경 금지**: 5/5 PASS 유지
  - 1h paper_sim 실험만 허용 (PAPER_SIM_STRATEGY_PARAMS)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **ROC_MIN_ABS 추가 하향 실험 금지**: 이미 0.1% 역효과 확인

### ⚠️ 주의 사항 (Cycle 331, 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 335)
- 테스트: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**, 표준): **0/20 PASS** (15사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
  - 주요 FAIL 원인: profit_factor < 1.5 (전체)
  - **NEW 진단**: max_hold_closes가 전체 거래의 ~50% 차지 → PF 저하 원인
- Bundle OOS BTC 4h (OFI 복원): **5/5 PASS** ← 이전 사이클 파라미터 복원 확인
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 335 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 335 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` ← Cycle 336 D(ML) 변경
- `cmf: {"buy_thresh": 0.10}`
