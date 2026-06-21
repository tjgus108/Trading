# Next Steps

_Last updated: 2026-06-21 (Cycle 337 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 337

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 335 | A+C+F | 청산이유 추적(sl/tp/max_hold), BTC CSV 갭 없음 확인, OFI imbalance_threshold 탐색 완료 |
| 336 | B+D+F | MAX_HOLD=48 실험(Sharpe 전 전략 개선), OFI buy_thresh=0.30(BTC개선/ETH악화), 0/20 PASS 16연속 |
| 337 | B+D+F | max_hold_candles_override=48(1h전용), OFI buy_thresh복원, 5/5 Bundle PASS 유지, 0/20 17연속 |

### 🎯 Cycle 338 작업 방향 (338 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): ETH/SOL 합성 데이터 품질 재확인

- **배경**: Cycle 337 Paper Sim에서 ETH 전략 성능 분산이 BTC 대비 큼
- **작업**: ETH/SOL synthetic CSV 기본 통계 확인
  - `data/historical/synthetic/` OHLCV 정상성 (NaN, 갭, 이상값)
  - BTC vs ETH vs SOL 상위 전략 순위 비교 (심볼별 상위 전략 다름 원인 파악)
  - 현재 Paper Sim 평균 수익률: BTC -3.82%, 전체 평균 분산 분석

#### B(리스크): atr_multiplier_tp 탐색 (3.5→2.5)

- **배경**: Cycle 337 F(리서치) 분석
  - 현재 SL=ATR×1.5, TP=ATR×3.5 → R:R=2.33:1
  - 수수료 포함 BEP WR ≈ 36%, 실측 WR ≈ 37-40% (여유 매우 얇음)
  - MAX_HOLD=48(1h) 적용 후 tp% 증가 예상 → TP 도달률 확인 필요
- **작업**: Paper Sim에서 `atr_multiplier_tp=2.5` vs `3.5` 비교
  - `paper_simulation.py`에서 engine 파라미터 변경
  - 주의: BEP WR이 36%→38%로 높아짐 → WR 37-40%에서 역효과 가능
  - 결과 분석: price_cluster, roc_ma_cross PF 변화 중심으로 평가
  - **MDD 20% 기준 유지 필수**

#### F(리서치): 1h 구조적 FAIL 원인 — 신호 품질 분석

- **배경**: 17사이클 연속 0/20 PASS, MAX_HOLD=48로도 PF < 1.5 돌파 못 함
- **작업**: price_cluster, roc_ma_cross의 8개 윈도우별 성능 분포 분석
  - 어느 윈도우에서 PASS 근접 (Sharpe≥0.5, PF≥1.2)?
  - FAIL 윈도우 공통점: 시장 국면 (trending/sideways/bearish)?
  - 신호 빈도 vs 승률 트레이드오프 분석 (`--verbose-windows` 옵션 활용)
- **참고**: Paper Sim에 `--verbose-windows` 옵션 있으면 활용

### ⚠️ 주의 사항 (Cycle 338)

- **max_hold_candles_override=48 유지**: `paper_simulation.py` engine에 고정, 절대 제거 금지
  - Bundle OOS engine에는 전달 안 함 (RollingOOSValidator → BacktestEngine 기본값 24 유지)
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
  - `timeframe="4h"` engine 전달 금지 → Sharpe 50% 하락, 전체 임계값 무효화 확인됨
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` ← Cycle 337 D(ML) 복원
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### ⚠️ 주의 사항 (Cycle 331, 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 337 결과)

| 지표 | Cycle 336 (MAX_HOLD=24) | Cycle 337 (MAX_HOLD=48) | 변화 |
|------|------------------------|------------------------|------|
| price_cluster Sharpe | 0.34 | 0.90 | +0.56 ↑ |
| roc_ma_cross Sharpe | -0.41 | 0.25 | +0.66 ↑ |
| frama Sharpe | N/A | 0.33 | 신규 top3 |
| OFI rank | 5 | 6 | -1 (buy_thresh 복원) |
| 1h PASS 수 | 0/20 | 0/20 | 변화 없음 (17연속) |
| Bundle OOS PASS | 5/5 | 5/5 | 유지 ✅ |

### 핵심 메트릭 (Cycle 337: MAX_HOLD 분리 아키텍처)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 337 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 337 변경)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원 (0.30→0.25 기본값)
- `cmf: {"buy_thresh": 0.10}`
