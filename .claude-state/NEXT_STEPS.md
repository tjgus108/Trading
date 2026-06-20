# Next Steps

_Last updated: 2026-06-20 (Cycle 334 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 334

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 332 | B+D+F | paper_sim --min-hold-bars CLI 추가, OFI v2 trend_span=15 실험→역효과 확인 복원 |
| 333 | C+B+F | data_utils 테스트+6, cooldown_suppressed 진단 필드, trend_span=25 실험→복원 |
| 334 | D+E+F | delta_window=5 실험→FAIL→복원, walk_forward lucky_fold 경고 추가, live_paper_trader 검증 |

### 🎯 Cycle 335 작업 방향 (335 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 테스트 커버리지 및 백테스트 품질 검증

- **배경**: 8425 tests 유지 중. 최근 walk_forward.py 코드 추가
- **작업**: walk_forward.py lucky_fold 경고 로직 테스트 추가
  - `test_bundle_oos_lucky_fold_warning()`: fold OOS > avg+1.5*std AND >5.0 시 WARNING 발생 검증
  - 테스트 파일: `tests/test_walk_forward_bundle.py` 또는 `tests/test_bundle_oos.py`

#### C(데이터): OFI v2 buy_thresh/sell_thresh 파라미터 탐색

- **배경**: delta_window 탐색 완료 (5/7 FAIL, 10 PASS,best). 다음 탐색 후보
- **작업**: `run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS 변경
  - `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` 실험
  - 목표: avg > 4.345 AND std < 0.907 (trend_span=20 delta_window=10 기준)
  - 역효과면 즉시 복원 (buy_thresh/sell_thresh 기본값 0.25/-0.25 유지)

#### F(리서치): OFI v2 파라미터 탐색 이력 정리

- **결론**: delta_window 그리드 탐색 완료
  - trend_span: 15(FAIL) < 25(PASS) < 20(PASS,best) — 완료
  - delta_window: 5(FAIL), 7(FAIL), 10(PASS,best) — 완료
  - 다음 후보: buy_thresh(0.25→0.30) 탐색

### ⚠️ 주의 사항 (Cycle 335)
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` (Cycle 334 복원 완료)
  - trend_span 그리드 완료: 15(FAIL) < 25(PASS) < 20(PASS,best)
  - delta_window 그리드 완료: 5(FAIL), 7(FAIL), 10(PASS,best)
  - 다음 탐색: buy_thresh=0.30 (신호 강화, 노이즈 억제 vs 저거래 위험)
- **walk_forward.py lucky_fold 경고**: Cycle 334 추가 (fold OOS >avg+1.5*std AND >5.0 → WARNING)
  - PASS/FAIL 로직 무변경, 순수 진단 목적
- **roc_ma_cross**: min_hold_bars=4 시 Sharpe 개선 (+0.57), 단 전략 고유 설정 미지원
- **price_cluster**: min_hold_bars=4 시 Sharpe 악화 (-0.87) → 기본값(0) 유지
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **ROC_MIN_ABS 추가 하향 실험 금지**: 이미 0.1% 역효과 확인

### 핵심 메트릭 (Cycle 334)
- 테스트: **8425 passed, 23 skipped** (회귀 없음, walk_forward.py 코드 추가)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (14사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, 1/8) ← 표준 파라미터
  - rank2: positional_scaling (Sharpe=0.00, Return=+1.97%, 1/8)
  - rank3: roc_ma_cross (Sharpe=-0.41, Return=+0.09%, 2/8)
- Bundle OOS BTC 4h (delta_window=5 실험 후 복원, 5-fold): **5/5 PASS** (기준 복원!)
  - order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1) ← delta_window=10 복원
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - vwap_cross: PASS (avg=3.047, std=1.437, rank4)
  - cmf: PASS (avg=2.508, std=1.888, rank5)
  - delta_window=5 실험 (FAIL): avg=2.962, std=3.570 — fold0 OOS=7.75 lucky fold + fold2 FAIL

### 핵심 메트릭 (Cycle 333, 이전)
- 테스트: **8425 passed, 23 skipped** (+6 신규, 회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**): **0/20 PASS** (13사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, 1/8) ← 표준 기준
- Bundle OOS BTC 4h: **5/5 PASS** (trend_span=25 실험 결과)
  - order_flow_imbalance_v2: PASS (avg=3.929, std=1.081) ← trend_span=25 실험
  - ⚠️ 파라미터 복원 완료 (trend_span=20) — Cycle 334에서 avg=4.345 복구 확인

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
