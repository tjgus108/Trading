# Next Steps

_Last updated: 2026-06-20 (Cycle 334 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 334

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 332 | B+D+F | paper_sim --min-hold-bars CLI 추가, OFI v2 trend_span=15 실험→역효과 확인 복원 |
| 333 | C+B+F | data_utils 테스트+6, cooldown_suppressed 진단 필드, trend_span=25 실험→복원 |
| 334 | D+E+F | delta_window=5 실험→FAIL(avg=2.962,std=3.570), live_paper_trader CSV fallback 검증, OFI 파라미터 탐색 완료 |

### 🎯 Cycle 335 작업 방향 (335 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 백테스트 품질 재검증

- **배경**: Paper Sim 14사이클 연속 0/20 PASS — profit_factor 1.5 미달이 주요 FAIL 원인
- **작업**: 상위 전략들의 FAIL 원인 집중 분석
  - price_cluster: PF=1.11 (목표 1.5) — BTC 1h 기준 개선 가능한지 분석
  - positional_scaling: PF=1.18 — 진입 조건 재검토
  - `src/backtest/engine.py` 슬리피지 모델 재검토 (adaptive_slippage 효과)
- **주의**: min_hold_bars 전략별 적용 금지 (전역 설정 변경하면 전체에 영향)

#### C(데이터): 시계열 데이터 커버리지 확인

- **배경**: SOL/ETH는 synthetic CSV만 있고 real data 없음 (BTC만 실거래소)
- **작업**: `data/historical/` 디렉토리 구조 점검
  - `data_utils.load_csv_ohlcv()` 경로 탐색 로직 재검토
  - SOL/ETH synthetic 데이터 품질 검사 (NaN, 극단값, 봉 연속성)
  - BTC 1h CSV 데이터 연장 가능 여부 확인 (현재 2023-01~2024-05, 12000 rows)

#### F(리서치): OFI v2 파라미터 탐색 결론 기록 + 다음 방향

- **결론**: OFI v2 최적 파라미터 `{"trend_span": 20, "delta_window": 10}` 확정
  - trend_span 그리드: 15(FAIL) < 25(PASS,3.929) < 20(PASS,best=4.345) ← 완료
  - delta_window 그리드: 5(FAIL,2.962) < 10(best,4.345) ← 완료
- **다음 탐색 방향**: OFI v2 `imbalance_threshold` 파라미터 확인
  - 현재 신호 발생 조건 분석: `cum_delta / total_vol` 임계값
  - 전략 소스 확인 후 파라미터화 여부 결정

### ⚠️ 주의 사항 (Cycle 335)
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` (복원 완료)
  - trend_span 그리드 탐색 완료: 15(FAIL) < 25(PASS) < 20(PASS,best)
  - delta_window 그리드 탐색 완료: 5(FAIL) < 10(best)
  - 다음 탐색: imbalance_threshold 확인 후 결정
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

### 핵심 메트릭 (Cycle 334)
- 테스트: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**, 표준): **0/20 PASS** (14사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, 1/8) — 표준 기준 복귀
  - rank2: roc_ma_cross (Sharpe=-0.41, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
  - 주요 FAIL 원인: profit_factor 1.5 미달 (전략 전반)
- Bundle OOS BTC 4h (delta_window=5 실험): **4/5 PASS** (복원 전)
  - order_flow_imbalance_v2: **FAIL** (avg=2.962, std=3.570) ← delta_window=5 역효과
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank1)
  - value_area: PASS (avg=3.069, std=0.085, rank2)
  - vwap_cross: PASS (avg=3.047, std=1.437, rank3)
  - cmf: PASS (avg=2.508, std=1.888, rank4)
  - ⚠️ 파라미터 복원 완료 → 다음 사이클 Bundle OOS 재실행 시 5/5 PASS 복구 예정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 334 복원)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 복원 (delta_window=5 실험 후, delta_window=10 기본값 최적 확정)

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
