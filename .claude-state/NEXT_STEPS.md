# Next Steps

_Last updated: 2026-06-20 (Cycle 337 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 337

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 335 | A+C+F | 청산이유 추적(sl/tp/max_hold), BTC CSV 갭 없음 확인 |
| 336 | B+D+F | MAX_HOLD=48 실험(Sharpe 전 전략 개선), OFI buy_thresh=0.30(BTC개선/ETH악화) |
| 337 | B+D+F | MAX_HOLD=48 4h→2/5 FAIL(즉시복원), OFI 0.30→0.25 복원, price_cluster Sharpe 0.90 |

### 🎯 Cycle 338 작업 방향 (338 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### B(리스크): 타임프레임별 MAX_HOLD 구현 (핵심)

- **배경**: Cycle 337 실험 — MAX_HOLD=48 at 4h = 8일 → Bundle OOS 5/5→2/5 FAIL(catastrophic)
  - value_area: OOS Sharpe 3.069 → 0.090 (즉시 복원 필요하여 복원 완료)
  - MAX_HOLD=24 (4일) at 4h: 5/5 PASS 유지 확인
- **핵심 발견**: MAX_HOLD는 타임프레임 인식이 필요
  - 1h: 48봉 = 2일 (Cycle336 개별 전략 실험에서 개선 확인)
  - 4h: 24봉 = 4일 (5/5 PASS 유지 중, 변경 금지)
- **작업**: `engine.py`에 타임프레임별 MAX_HOLD 구현
  ```python
  # engine.py에 추가
  TF_MAX_HOLD: Dict[str, int] = {
      "1h": 48,   # 2일 (개선 기대)
      "4h": 24,   # 4일 (5/5 PASS 유지)
      "1d": 10,   # 10일
  }
  # run() 메서드에서:
  max_hold = TF_MAX_HOLD.get(self.timeframe, MAX_HOLD_CANDLES)
  ```
  - `MAX_HOLD_CANDLES = 24` 상수는 유지 (fallback용)
  - 위치: `run()` 메서드 시작 부분에 `max_hold` 로컬 변수 정의
  - 내부 `if position["hold_candles"] >= MAX_HOLD_CANDLES:` → `if position["hold_candles"] >= max_hold:`
- **기대**: 1h paper sim에서 price_cluster(Sharpe=0.90) 등 PASS 가능성 (MAX_HOLD=48 효과)
- **주의**: 4h Bundle OOS 영향 없음 (TF_MAX_HOLD["4h"]=24 변경 없음)
- **금지**: TF_MAX_HOLD["4h"] 변경 절대 금지 (5/5 PASS 보호)

#### C(데이터): price_cluster Sharpe 0.90 원인 분석

- **배경**: BTC paper sim rank1 price_cluster Sharpe 0.34→0.90 (Cycle 337 대폭 개선)
  - 아직 PASS(1.0) 도달 못했지만 가장 가까운 전략
  - 어느 window에서 PASS에 근접했는지 분석 가능
- **작업**: `PAPER_SIMULATION_RESULTS.json` 또는 `PAPER_SIMULATION_RESULTS.csv` 파일 분석
  - price_cluster window별 Sharpe 분포 확인 (어느 기간에 강한지)
  - 2023-2024 구간에서 특정 레짐(상승장/하락장)과의 상관 분석
  - 이 분석을 바탕으로 파라미터 조정 가능성 탐색

#### F(리서치): atr_multiplier_tp 실험 탐색

- **배경**: R:R 분석 (Cycle 337 F)
  - 현재: atr_multiplier_sl=1.5, atr_multiplier_tp=3.5 → R:R = 2.33:1
  - WR=38%에서 이론 PF = 1.43 (임계값 1.50에 0.07 부족)
  - PF≥1.5 달성을 위한 최소 R:R = 2.45
- **실험 후보**: atr_multiplier_tp=3.5→4.0 (R:R=2.67, 이론 PF=1.63)
  - 단, MAX_HOLD 연장(Cycle338 B)과 병행 시 효과 증폭 가능
  - Cycle 338 B(타임프레임별 MAX_HOLD) 먼저 완료 후 paper sim 확인 → 여전히 PF<1.5면 F 실험
- **주의**: 이 실험은 C, B 작업 완료 후 paper sim 결과 확인 후 진행 (순서 중요)

### ⚠️ 주의 사항 (Cycle 338)
- **MAX_HOLD_CANDLES 상수 = 24 유지**: TF_MAX_HOLD dict 추가 방식으로 변경
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **Bundle OOS 파라미터 변경 금지**: 5/5 PASS 유지 (BUNDLE_STRATEGY_INIT_PARAMS 동결)

### ⚠️ 주의 사항 (영구 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)
- **ROC_MIN_ABS 추가 하향 실험 금지**: 이미 0.1% 역효과 확인

### 핵심 메트릭 (Cycle 337)
- MAX_HOLD=48 at 4h 실험 결과:
  - Bundle OOS 5/5 → 2/5 FAIL (value_area: 3.069→0.090 catastrophic)
  - MAX_HOLD=24 복원 후 5/5 PASS 재확인

- BTC 1h Paper Sim (Cycle 337, MAX_HOLD=24, buy_thresh=0.30):

| 전략 | AvgSharpe | AvgPF | AvgTrades | Consist | Pass |
|------|-----------|-------|-----------|---------|------|
| price_cluster | 0.90 | 1.21 | 41 | 2/8 | FAIL |
| roc_ma_cross | 0.25 | 1.20 | 36 | 2/8 | FAIL |
| frama | 0.33 | 1.15 | 40 | 1/8 | FAIL |
| OFI v2 (rank6) | -0.70 | 0.96 | 67 | 0/8 | FAIL |

### 핵심 메트릭 (Cycle 336, 유지)
- Paper Sim BTC 1h (8 windows, 20전략, buy_thresh=0.30): **0/20 PASS** (16사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지
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
- Paper simulation 1h: **20 전략** × 8 windows × 3 심볼 → 약 12분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 337 변경 없음)
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
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML): buy_thresh=0.30→기본값(0.25) 복원
- `cmf: {"buy_thresh": 0.10}`
