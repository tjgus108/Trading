# Next Steps

_Last updated: 2026-06-21 (Cycle 341 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 341

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 339 | D+E+F | 레짐필터 역효과(roc_ma_cross -0.43→롤백), 슬리피지 임계값 2→3%, 0/20 19연속 |
| 340 | A+C+F | IS/OOS 레짐 진단 추가, roc_ma_cross 필터 롤백 확인(+0.34↑), 0/20 20연속 |
| 341 | B+D+F | W5 구조적 FAIL 확인, IS→OOS 상관관계 정량화, loss_scale 추적 추가, 0/20 21연속 |

### 🎯 Cycle 342 작업 방향 (342 mod 5 = 2 → C(데이터) + E(실행) + A(품질))

#### C(데이터): 데이터 품질 검증 및 피처 엔지니어링 개선

- **배경**: 현재 BTC 1h 12000행, ETH/SOL 합성 데이터. 4h CSV 없음 (리샘플)
- **작업**:
  - BTC 1h.csv의 OHLCV 정합성 재확인 (가격 스파이크, gap 검사)
  - paper_simulation.py의 `enrich_indicators()` 함수 검토
    - Donchian, MACD 계산 정확성 확인
    - ATR14 0값 발생 빈도 확인 (`signals_skipped_atr0` 분석)

#### E(실행): 진입 슬리피지 분포 분석 + 고변동성 구간 최적화

- **배경**: Cycle 341 B 분석: volatility=0.054(낮음)인 W5에서 price_cluster PF<1.5
  - 고변동성 구간과 저변동성 구간에서 슬리피지 레짐 분포 차이 확인 필요
  - 새로 추가된 `loss_scale_half_count`, `loss_scale_full_count` 활용
- **작업**:
  - paper_sim에서 slippage_regime_counts와 loss_scale_counts 윈도우별 비교
  - 고변동성(W6, volatility=0.104) vs 저변동성(W5, 0.054) 슬리피지 분포 비교

#### A(품질): price_cluster PF 개선 방향 탐색

- **배경**: price_cluster 8개 윈도우 중 7개 FAIL. 주요 FAIL 원인: PF<1.5(W5), sharpe<1.0(others)
  - W6만 PASS (Sharpe=3.78, PF 확인 필요)
  - price_cluster._BOUNCE_PCT=0.01, _CLOSE_WINDOW=50, _N_BINS=5 현재값
- **작업**:
  - W6 PASS 원인 분석: 슬리피지 레짐, 손실 스케일 사용 현황
  - loss_scale_half/full_count를 통한 스케일링 영향 정량화

### ⚠️ 주의 사항 (Cycle 342)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: `atr_ratio < 0.03 * tf_scale`
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 340 확정)

| 지표 | Cycle 339 | Cycle 340 | 변화 |
|------|-----------|-----------|------|
| roc_ma_cross Sharpe | -0.43 | **+0.34** | +0.77 ↑↑ (레짐필터 롤백 효과 확인) |
| roc_ma_cross Trades | 18 | 36 | +100% (신호 복구) |
| roc_ma_cross Consistency | 0/8 | **2/8** | 개선 ↑ |
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| 1h PASS 수 | 0/20 (19연속) | **0/20 (20연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### IS/OOS 레짐 진단 결과 (Cycle 340 신규)

| Window | IS end-state | OOS dominant | mkt | price_cluster | roc_ma_cross |
|--------|-------------|--------------|-----|---------------|--------------|
| W1 | TREND_UP | TREND_UP | bull | -1.43 FAIL | 4.04 PASS |
| W2 | TREND_UP | RANGING | bull | 0.11 FAIL | 3.84 PASS |
| W3 | RANGING | RANGING | bear | 0.00 FAIL | -0.04 FAIL |
| W4 | RANGING | RANGING | bear | -0.41 FAIL | -2.01 FAIL |
| W5 | RANGING | RANGING | sideways | 0.99 FAIL | -3.77 FAIL |
| W6 | RANGING | RANGING | sideways | **3.78 PASS** | -0.28 FAIL |
| W7 | RANGING | RANGING | bull | -0.08 FAIL | -1.12 FAIL |
| W8 | TREND_UP | RANGING | bull | 0.21 FAIL | -2.05 FAIL |

- price_cluster 최적 환경: RANGING+RANGING+sideways (W6)
- roc_ma_cross 최적 환경: IS=TREND_UP + bull market momentum (W1, W2)
- 근본 문제: 8개 윈도우 중 IS=TREND_UP인 구간은 W1, W2, W8뿐 → roc_ma_cross에 불리한 데이터 구조

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

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
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요 (BTC only)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)
- 이유: 개별 봉 수준 TREND_UP 필터 → roc_ma_cross trades 57→18, Sharpe +0.32→-0.43 역효과 확인
- 윈도우 수준 레짐 매칭 방식은 Cycle 341 D(ML)에서 검토 예정
