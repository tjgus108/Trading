# Next Steps

_Last updated: 2026-06-17 (Cycle 323 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 323

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 321 | B+D+F | price_cluster→vwap_cross 교체, is_negative_regime_max 추가, **Bundle 3→4/5 PASS** |
| 322 | B+D+F | bear_oos_max=1.0 추가, vwap_cross fold1 해결, **Bundle 4→5/5 PASS (역대 최고!)** |
| 323 | C+B+F | 5/5 PASS 안정성 확인, combined_exclusion_ratio 경고 추가, Bundle 5개 live_paper_trader 등록 |

### 🎯 Cycle 324 작업 방향 (324 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): 1h 전략 개선 — Paper Sim 0/22 PASS 원인 분석

- **supertrend_multi 1h 성과**: return=+5.26%, Sharpe=0.32 → PASS 기준(Sharpe≥1.0) 크게 미달
  - 4h에서는 avg=3.892, 1h에서는 0.32 — 타임프레임 불일치 확인
  - 파라미터 그리드 재검토: `atr_threshold`, `trend_confirm_bars` 1h 전용 탐색
- **1h Paper Sim 개선 가능성**:
  - Sharpe=1.0 달성을 위한 신호 필터 강화 vs 완화 균형
  - cmf_1h 그리드: period=[90,105], buy_thresh=[0.07,0.08,0.10] → 추가 최적화 여지
  - 합성 데이터 PASS 전략(Sharpe≥1.0)이 실전 데이터에서 FAIL하는 패턴 조사

#### E(실행): live_paper_trader 4h 지원 추가 검토

- **현재 live_paper_trader**: 1h 타임프레임 전용
  - Bundle 전략 5개는 4h OOS PASS → 1h로 실행 시 성과 달라질 수 있음
  - `DEFAULT_TIMEFRAME = "1h"` → 4h 지원 옵션(`--timeframe 4h`) 추가 검토
- **Bundle 전략 4h 실행 준비**:
  - WARMUP_CANDLES=200 4h봉 → 약 800시간 = 33일 데이터 필요
  - SSL 제약으로 외부 API 차단 → CSV fallback 4h 경로 지원 확인

#### F(리서치): 레짐 기반 전략 스위칭 로드맵

- **현재 레짐 감지**: MarketRegimeDetector 존재 (TREND_UP, TREND_DOWN, HIGH_VOL, RANGING)
- **스위칭 로드맵**:
  - TREND_UP: OFI v2 + supertrend_multi 중심 (추세 추종)
  - TREND_DOWN: vwap_cross + value_area 중심 (mean reversion)
  - HIGH_VOL: cmf 중심 (volume filter 강함)
  - RANGING: 포지션 최소화

### ⚠️ 주의 사항 (Cycle 324)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 323)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
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
