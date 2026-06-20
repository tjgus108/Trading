# Next Steps

_Last updated: 2026-06-20 (Cycle 339 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 339

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 337 | B+D+F | MAX_HOLD=48 4h→2/5 FAIL(즉시복원), OFI 0.30→0.25 복원, price_cluster Sharpe 0.90 |
| 338 | C+B+F | TF_MAX_HOLD 구현 + walk_forward.py 버그 수정 (max_hold_override), price_cluster 분석 |
| 339 | D+F | atr_multiplier_tp=4.0 실험 → bundle OOS 1/5 FAIL → 즉시 revert; ML 재훈련 FAIL (test_acc < 0.55) |

### 🎯 Cycle 340 작업 방향 (340 mod 5 = 0 → D(ML) + E(실행) + F(리서치))

#### F(리서치): R:R 개선 대안 탐색 (atr_multiplier_tp=4.0 실패 후)

- **배경**: atr_multiplier_tp=4.0 실험 결과
  - Bundle OOS 1/5 PASS (catastrophic regression): cmf/OFI/vwap_cross/value_area FAIL
  - 즉시 revert → 5/5 PASS 복원
  - **결론**: TP 원거리화가 4h 번들 전략 구조와 충돌 (청산 타이밍 변화)
- **대안 실험 후보**: (다음 중 하나 선택)
  1. `atr_multiplier_sl=1.5→1.2` (SL 좁히기, R:R=2.92) — 단, WR 하락 가능
  2. `min_hold_bars=4` 1h 효과 분석 (재진입 쿨다운, rank1 price_cluster 개선 가능)
  3. `price_cluster` 트렌드 필터 추가 (W1/W2 bull 시장 실패 방지) — ATR slope 또는 EMA200 기반
- **주의**: 어떤 실험도 bundle OOS 5/5 PASS 보호 최우선

#### D(ML): ML 피처 엔지니어링 개선

- 재훈련 FAIL 원인: 심각한 과적합 (train ~0.76 vs test ~0.46-0.51)
- **다음 시도 방향**:
  1. 피처 수 줄이기 (현재 상위 피처: macd_hist, volatility_20, nr_atr_ratio, ema_ratio)
  2. 시계열 특성 강화: lag 피처 추가 또는 rolling std
  3. 앙상블 다양화: GradientBoosting 추가
- OFI v2 1h paper sim 성능 여전히 부진: rank8, Sharpe=-0.70

#### E(실행): Paper Trading 모드 점검

- live_paper_trader.py 상태 확인 (오류/미완성 부분 점검)
- SSL 인터셉션 환경에서 demo 모드 안정성 테스트

### ⚠️ 주의 사항 (영구 유지)

- **atr_multiplier_tp=3.5 고정**: tp=4.0 실험 → bundle OOS 1/5 FAIL 확인됨 (Cycle 339). 더 이상 tp 상향 실험 금지.
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)
- **ROC_MIN_ABS 추가 하향 실험 금지**: 이미 0.1% 역효과 확인
- **MAX_HOLD_CANDLES = 24 fallback 유지**: TF_MAX_HOLD dict 추가 방식으로 변경됨
- **RollingOOSValidator annualization 주의**: bundle OOS는 timeframe="1h" 기준 Sharpe 사용 (1h annualization)
  - timeframe="4h"로 변경 시 Sharpe가 2x 반토막 → 모든 임계값 재조정 필요
  - 현재 max_hold_override=MAX_HOLD_CANDLES로 역호환성 유지

### 핵심 메트릭 (Cycle 339)

- **atr_multiplier_tp=4.0 실험**: Bundle OOS 1/5 PASS → 즉시 revert → 5/5 PASS 복원
- **ML 모델 재훈련**: BTC/ETH/SOL 모두 FAIL (test_acc 0.45-0.51 < 0.55 임계값)
  - 과적합 심각: train ~0.76 vs test ~0.46-0.51
  - 모든 심볼에서 ADWIN drift confirmed (레짐 변화 감지)

### 핵심 메트릭 (Cycle 338, 유지)

- BTC 1h Paper Sim (8 windows, 20전략, MAX_HOLD=48, buy_thresh=0.25): **0/20 PASS** (18사이클 연속)
  - rank1: price_cluster (Sharpe=0.90, Return=+5.60%, PF=1.21, 2/8)
  - rank2: roc_ma_cross (Sharpe=0.25, PF=1.20, 2/8)
  - rank3: frama (Sharpe=0.33, PF=1.15, 1/8)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지 (Cycle 339 revert 후 재확인)
  - rank1: order_flow_imbalance_v2 (avg=4.345)
  - rank2: supertrend_multi (avg=3.892)
  - rank3: value_area (avg=3.069)
  - rank4: vwap_cross (avg=3.047)
  - rank5: cmf (avg=2.508)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows × 3 심볼 → 약 12분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 339 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 이후 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 337 D(ML) 변경 이후 유지)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← buy_thresh=0.25 (기본값)
- `cmf: {"buy_thresh": 0.10}`
