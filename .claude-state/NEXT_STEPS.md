# Next Steps

_Last updated: 2026-06-20 (Cycle 338 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 338

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 336 | B+D+F | MAX_HOLD=48 실험(Sharpe 전 전략 개선), OFI buy_thresh=0.30(BTC개선/ETH악화) |
| 337 | B+D+F | MAX_HOLD=48 4h→2/5 FAIL(즉시복원), OFI 0.30→0.25 복원, price_cluster Sharpe 0.90 |
| 338 | C+B+F | TF_MAX_HOLD 구현 + walk_forward.py 버그 수정 (max_hold_override), price_cluster 분석 |

### 🎯 Cycle 339 작업 방향 (339 mod 5 = 4 → D(ML) + F(리서치))

#### F(리서치): atr_multiplier_tp 실험 (Cycle 338에서 연기됨)

- **배경**: R:R 분석
  - 현재: atr_multiplier_sl=1.5, atr_multiplier_tp=3.5 → R:R = 2.33:1
  - WR=38%에서 이론 PF = (0.38×2.33)/(0.62×1.0) = 1.43 (임계값 1.50에 0.07 차이)
  - Paper Sim rank1 price_cluster PF=1.21 (실제 PF < 이론 PF → 슬리피지+수수료 영향)
- **실험**: `engine.py` `atr_multiplier_tp=3.5→4.0`
  - R:R=2.67, 이론 PF = (0.38×2.67)/(0.62) = 1.63 → PASS 가능성
  - 단, TP 원거리화로 WR 감소 가능 → 순 효과 확인 필요
- **절차**:
  1. `engine.py` `atr_multiplier_tp: float = 3.5` → `4.0` 변경
  2. Paper sim 실행 (3 symbols × 20전략 × 8 windows)
  3. Bundle OOS 4h 실행 (5/5 PASS 유지 확인)
  4. PF 개선 확인 → keep / FAIL → revert
- **주의**: Bundle OOS 5/5 PASS 보호가 최우선

#### D(ML): ML 모델 상태 점검

- Cycle 338 paper sim에서 ADWIN drift detected (재훈련 권고)
- ML 모델 재훈련 또는 파라미터 조정 검토
- OFI v2 성능 점검 (rank8, Sharpe=-0.70)

### ⚠️ 주의 사항 (영구 유지)

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

### 핵심 메트릭 (Cycle 338)

- TF_MAX_HOLD 1h=48 효과: **없음** (SL/TP 선행 청산)
- price_cluster 분석: 횡보장 전략, W6(sideways)=Sharpe 3.167 PASS, W1(bull+143%)=Sharpe -0.546 FAIL

- BTC 1h Paper Sim (Cycle 338, MAX_HOLD=48):

| 전략 | AvgSharpe | AvgPF | AvgTrades | Consist | Pass |
|------|-----------|-------|-----------|---------|------|
| price_cluster | 0.90 | 1.21 | 41 | 2/8 | FAIL |
| roc_ma_cross | 0.25 | 1.20 | 36 | 2/8 | FAIL |
| frama | 0.33 | 1.15 | 40 | 1/8 | FAIL |

### 핵심 메트릭 (Cycle 337, 유지)

- Paper Sim BTC 1h (8 windows, 20전략, buy_thresh=0.25): **0/20 PASS** (18사이클 연속)
  - rank1: price_cluster (Sharpe=0.90, Return=+5.60%, PF=1.21, 2/8)
  - rank2: roc_ma_cross (Sharpe=0.25, PF=1.20, 2/8)
  - rank3: frama (Sharpe=0.33, PF=1.15, 1/8)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.957)
  - rank2: supertrend_multi (avg=3.892, std=1.286)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows × 3 심볼 → 약 12분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 338 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 337 D(ML) 변경)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← buy_thresh=0.25 (기본값)
- `cmf: {"buy_thresh": 0.10}`
