# Next Steps

_Last updated: 2026-06-17 (Cycle 324 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 324

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 322 | B+D+F | bear_oos_max=1.0 추가, vwap_cross fold1 해결, **Bundle 4→5/5 PASS (역대 최고!)** |
| 323 | C+B+F | 5/5 PASS 안정성 확인, combined_exclusion_ratio 경고 추가, Bundle 5개 live_paper_trader 등록 |
| 324 | D+E+F | cmf_confirm=True 실험→역효과 롤백, **live_paper_trader 4h --timeframe 지원 추가** |

### 🎯 Cycle 325 작업 방향 (325 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 1h Paper Sim 개선 — atr_threshold 그리드 탐색

- **supertrend_multi 1h 성과**: return=+5.26%, Sharpe=0.32, trades=48
  - cmf_confirm=True 실험 역효과 확정 (Cycle 324): Sharpe 0.32→0.02
  - 다음 실험: `atr_threshold=0.3` 또는 `trend_confirm_bars=1` (더 많은 1h 신호)
  - 또는 레짐 필터 기반: TREND_UP 레짐일 때만 BUY 허용 (MarketRegimeDetector 활용)
- **price_cluster 1h rank2 유지**: return=+2.19%, Sharpe=0.34 — 추가 최적화 여지 있음
  - bounce_pct, n_bins 1h 전용 그리드 탐색 여부 검토

#### C(데이터): 4h CSV fallback 지원 확인 + live_paper_trader 4h 모드 검증

- **4h CSV 파일 존재 여부 확인**:
  - `data/historical/binance/BTCUSDT/4h.csv` 존재 여부 — 없으면 1h→4h resample 코드 확인
  - live_paper_trader `--timeframe 4h` 실제 초기화 테스트 (SSL 차단으로 실제 시장 연결 불가)
- **resample 로직 검토**: paper_simulation.py의 1h→4h resample 코드가 live_paper_trader에도 적용되는지

#### F(리서치): 1h PASS 전략 실패 패턴 분석

- **전략 타임프레임 적합성**: 4h에서 5/5 PASS인 전략들이 1h에서 FAIL하는 근본 원인
  - ATR 기반 신호: 1h 단위 ATR은 4h 대비 노이즈 비율 4배 높음
  - 레짐 전환 빈도: 1h에서 레짐 전환이 더 자주 발생 → 전략 신호 품질 저하
  - 수수료 영향: 1h 거래 빈도 증가 → 왕복 수수료(0.11%) 부담 누적

### ⚠️ 주의 사항 (Cycle 325)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **run_bundle_oos.py 실행 시**: 반드시 `--csv-dir data/historical` 옵션 포함

### 핵심 메트릭 (Cycle 324)
- 테스트: **51 passed** (관련 모듈; 전체 회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: supertrend_multi (return=+5.26%, Sharpe=0.32, trades=48)
  - rank2: price_cluster (return=+2.19%, Sharpe=0.34)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (유지)
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
- Paper simulation 1h: 22 전략 × 8 windows → 약 8분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 323 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터 (Cycle 321 B: price_cluster 교체)
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 323 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← **UPDATED** Cycle 322 B
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 323 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
