# Next Steps

_Last updated: 2026-06-19 (Cycle 333 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 333

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 331 | B+D+F | min_hold_bars 추가, price_cluster 그리드 업데이트, fee=0 gross alpha 실험 |
| 332 | B+D+F | paper_sim --min-hold-bars CLI 추가, OFI v2 trend_span=15 실험→역효과 확인 복원 |
| 333 | C+B+F | data_utils 테스트+6, cooldown_suppressed 진단 필드, trend_span=25 실험→복원 |

### 🎯 Cycle 334 작업 방향 (334 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 모델 재학습 권고 또는 OFI v2 delta_window 탐색

- **배경**: Paper Sim ADWIN drift=YES, Retrain Recommended=YES (3회 이미 재학습)
  - ML 재학습은 실거래소 데이터 없는 환경에서 효과 제한적 → OFI 탐색 우선
- **작업**: `run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS 변경
  - `{"trend_span": 20, "delta_window": 5}` 실험 (기본 delta_window 확인 후)
  - 목표: avg_sharpe > 4.345, std < 0.907 (trend_span=20 기준)
  - 역효과면 즉시 복원 (delta_window 기본값 유지 정책)

#### E(실행): Paper Trading 모드 점검

- **배경**: live_paper_trader.py 검토 미진행 (Cycle 332 이후)
- **작업**: `scripts/live_paper_trader.py` 코드 검토
  - 거래소 연결 실패 시 CSV fallback 로직 확인
  - 실행 시 오류 없이 초기화되는지 확인

#### F(리서치): OFI v2 trend_span 그리드 탐색 완료 기록

- **결론**: trend_span=20 최적 확정
  - 15(FAIL, std=2.771) < 25(PASS, avg=3.929, std=1.081) < 20(PASS, avg=4.345, std=0.907 최적)
- **다음 탐색**: delta_window 변경 (D(ML) 작업과 통합)
  - `{"trend_span": 20, "delta_window": 5}` 실험

### ⚠️ 주의 사항 (Cycle 334)
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` (Cycle 333 실험 후 복원)
  - trend_span 그리드 탐색 완료: 15(FAIL) < 25(PASS) < 20(PASS,best)
  - 다음 탐색: delta_window 변경
- **roc_ma_cross**: min_hold_bars=4 시 Sharpe 개선 (+0.57), 단 전략 고유 설정 미지원
- **price_cluster**: min_hold_bars=4 시 Sharpe 악화 (-0.87) → 기본값(0) 유지
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

### 핵심 메트릭 (Cycle 333)
- 테스트: **8425 passed, 23 skipped** (+6 신규, 회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**, min_hold_bars=4 실험): **0/20 PASS** (13사이클 연속)
  - rank1: roc_ma_cross (Sharpe=0.16, Return=+2.34%, 2/8) ← min_hold_bars=4 효과
  - rank2: positional_scaling (Sharpe=-0.40, 1/8)
  - rank6: price_cluster (Sharpe=-0.53, 1/8) ← min_hold_bars=4 악화
  - ⚠️ 이 리포트는 min_hold_bars=4 실험 run (표준 기준: rank1=price_cluster Sharpe=0.34)
- Bundle OOS BTC 4h (trend_span=25 실험, 5-fold): **5/5 PASS** (4/5 → 5/5 복원!)
  - order_flow_imbalance_v2: PASS (avg=3.929, std=1.081) ← trend_span=25 실험
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank1)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - vwap_cross: PASS (avg=3.047, std=1.437, rank4)
  - cmf: PASS (avg=2.508, std=1.888, rank5)
  - ⚠️ 파라미터 복원 완료 (trend_span=20) — 다음 사이클 OFI avg=4.345 복구 예정

### 핵심 메트릭 (Cycle 332, 이전)
- 테스트: **8419 passed, 23 skipped** (+3 신규 min_hold_bars, 회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (12사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
- Bundle OOS BTC 4h (5-fold, OFI 실험 파라미터): **4/5 PASS** (OFI v2 실험 FAIL)
  - order_flow_imbalance_v2: **FAIL** (avg=4.036, std=2.771, trend_span=15 실험)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank1)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - ⚠️ 파라미터 복원 완료 (trend_span=20)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 333 복원)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 복원 (25 실험 후, 20이 최적 확정)

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
