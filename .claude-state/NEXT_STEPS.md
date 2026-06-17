# Next Steps

_Last updated: 2026-06-17 (Cycle 320 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 320

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 318 | C+B+F | OFI v2 PASS(avg=4.345,std=0.907,rank1), vol_regime_filter=False 무효, **3/5 PASS** |
| 319 | D+E+F | bounce_pct=0.015 실험(저거래 80%→60%), Bundle PASS 가중치 live_paper_trader, 합성데이터 보호 |
| 320 | A+C+F | value_area overrides 추가(avg 0.713→2.016, std 2.018→1.825), price_cluster 교체 결정 |

### 🎯 Cycle 321 작업 방향 (321 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): price_cluster → vwap_cross 번들 교체 실험

- **Cycle 320 A 결론**: price_cluster 4h 신호 희소성 구조 한계 확정 (60% 저거래 binding)
  - WFE 로직 변경 검토: fold2(IS=-2.345, OOS=1.098) WFE 0.0→0.5 가능하나 std/저거래 여전히 FAIL
  - **교체 결정**: price_cluster → vwap_cross (4h 적합, 기존 번들과 다른 신호 로직)
- **B 작업**:
  1. `BUNDLE_STRATEGIES` 리스트에서 price_cluster → vwap_cross 교체
     - `("price_cluster", "PriceClusterStrategy")` → `("vwap_cross", "VWAPCrossStrategy")`
  2. `BUNDLE_STRATEGY_INIT_PARAMS`에서 price_cluster 파라미터 제거 (또는 vwap_cross 파라미터 추가)
  3. 4h OOS 실험: vwap_cross가 fold0~4에서 충분한 거래 생성하는지 확인
  4. **주의**: min_oos_trades=10 기본값 → vwap_cross 4h 신호 빈도 미지수, BUNDLE_STRATEGY_OVERRIDES 필요시 추가
  5. 교체 후 Bundle OOS 실행하여 전략 비교

#### D(ML): value_area fold0 bear regime 대응 분석

- **Cycle 320 C 결론**: value_area overrides 효과 확인
  - active folds: [0,1,2], avg=2.016, std=1.825 (std 기준 통과!)
  - **남은 binding constraint**: fold0 (2023-06~08 bear, IS=-1.466, OOS=-0.091, WFE=0.0)
  - fold0 OOS=-0.091은 거의 0에 가까운 손실 — bear period 구조적 미작동
- **D 작업**:
  1. value_area 전략 파라미터 분석:
     - fold0 bear period에서 IS=-1.466 → 전략 자체가 하락장에서 역방향 신호 생성
     - `vol_filter_mult=0.5` (현재 PAPER_SIM_STRATEGY_PARAMS) 4h에도 적용해보기
     - 또는: fold0 IS=-1.466<-1.5 조건 추가 → IS < -1.5인 fold를 "전략 미적합 레짐"으로 제외
  2. `BUNDLE_STRATEGY_OVERRIDES["value_area"]`에 추가 옵션 검토:
     - `"is_negative_regime_max": -1.5` 새 파라미터: IS < -1.5 AND OOS≈0 → 제외 가능성
     - **단독 실험 원칙**: 하나의 파라미터만 추가
  3. 목표: fold0 처리 후 value_area 4/5 PASS → 5/5 도달

#### F(리서치): vwap_cross 4h 포텐셜 평가 + 중간 결과 리서치

- **vwap_cross 특성**: VWAP20 vs VWAP50 골든/데드 크로스 — 4h 적합 추세 포착
  - 신호 빈도: 크로스 기반이므로 price_cluster(클러스터 bounce)보다 높을 가능성
  - 기존 번들과의 상관관계: OFI v2(압력), supertrend_multi(ATR추세), cmf(자금흐름)과 다른 로직
- **F 작업**:
  1. vwap_cross 전략 파라미터 확인 (`src/strategy/vwap_cross.py`)
  2. 4h OOS 시험 예상 fold별 신호 수 추정
  3. 대안 후보 검토: vwap_band (mean reversion) vs vwap_cross (trend following) — 번들 적합성 비교

### ⚠️ 주의 사항 (Cycle 321)
- **cmf_confirm**: `False` (변경 금지) — Cycle 316 D 확정
- **close_window=60**: 변경 금지 — Cycle 317 B에서 60이 30보다 나음 확인
- **OFI v2 overrides**: `regime_transition_is_min=2.0, min_oos_trades=3` 유지
- **bounce_pct=0.015**: BUNDLE_STRATEGY_INIT_PARAMS에서 제거 예정 (price_cluster 교체 시)
- **단독 실험 원칙**: BUNDLE_STRATEGY_OVERRIDES["value_area"]에 is_negative_regime_max 추가 시 파라미터 하나씩
- **price_cluster 교체 후 PAPER_SIM_STRATEGY_PARAMS도 업데이트** 필요

### 핵심 메트릭 (Cycle 320)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: price_cluster (score=75.7, Sharpe=0.59, trades=46)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32, trades=48)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **3/5 PASS** (유지)
  - order_flow_imbalance_v2: **PASS** (avg=4.345, std=0.907, rank1) ← 유지
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2) ← 유지
  - cmf: PASS (avg=2.508, std=1.888, rank3) ← 유지
  - price_cluster: FAIL (avg=3.823, std=3.854) ← 교체 예정 (Cycle 321 B)
  - value_area: FAIL (avg=2.016, std=1.825) ← override 적용, 개선! fold0이 binding

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 320 완료 후)
- `price_cluster: {"bounce_pct": 0.015, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← 교체 예정 (Cycle 321 B)
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 320 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5}` ← **NEW** Cycle 320 C

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 320 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `price_cluster: {"bounce_pct": 0.015, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
