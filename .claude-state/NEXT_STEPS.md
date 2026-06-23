# Next Steps

_Last updated: 2026-06-23 (Cycle 349 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 349

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 347 | B+D+F | manager.py evaluate()에 RANGING 매크로 실전 연동, 0/20 27연속 |
| 348 | C+B+F | ETH synthetic HL 2.88x 과장 수정 (4.3%→2.12%), 0/20 28연속 |
| 349 | D+E+F | 4h max_hold=24 우세 확인, --max-hold-override 추가, dema_cross HIGH% 원인 확정 |

### 🎯 Cycle 350 작업 방향 (350 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 4h paper_sim 전체 실행 및 PASS 기준 재검토

- **배경**: Cycle 349에서 max_hold=24 시 price_cluster 4h Sharpe=2.26, 4h 수수료 드래그 1/4
  - 4h PASS 기준: Sharpe >= 1.0, PF >= 1.5, Trades >= 15, MDD <= 20% — 1h와 동일
  - max_hold=24봉 now default for 4h paper_sim (Cycle 349 E 변경 반영)
- **작업**:
  - `python3 scripts/paper_simulation.py --csv-dir data/historical --timeframe 4h` 실행 (전략 전체)
  - PASS 전략 있으면 해당 파라미터/전략명을 BUNDLE_STRATEGY_INIT_PARAMS에 반영 검토
  - 4h에서 trades < 15인 전략들: 신호 조건 완화 또는 min_trades 기준 재검토

#### C(데이터): SOL 합성 데이터 vol_spike_prob 보정

- **배경**: SOL synthetic HIGH%(>=3%) = 54% — BTC 실제 0.7% 대비 77배
  - vol_spike_prob=0.35, daily_vol=0.055 (SOL 본질적 고변동성)
  - 실제 SOL 데이터 없어 검증 어렵지만 54%는 과도할 수 있음
- **작업**:
  - generate_garch_csv.py `SYMBOL_PARAMS["SOL"]["vol_spike_prob"]` 0.35→0.25 조정 검토
  - 재생성 후 SOL HIGH% 목표: 40% 이하
  - ETH Cycle 348 수정과 동일한 절차로 SOL SOLUSDT/1h.csv 재생성

#### F(리서치): 4h PASS 전략 존재 시 Bundle OOS 연동 가능성 검토

- **배경**: Cycle 349 4h paper_sim에서 supertrend_multi Sharpe=2.20, price_cluster Sharpe=2.26
  - Bundle OOS는 이미 supertrend_multi PASS (5/5)
  - price_cluster는 Bundle OOS에 없음 — 연동 가능성 분석 필요
- **작업**:
  - price_cluster 전략 특성 분석: 4h에서 trades=10 (Bundle OOS 최소 기준 10 충족?)
  - `run_bundle_oos.py` 비공식 테스트: price_cluster 4h OOS 검증 가능 여부
  - 리서치: 4h 전략이 1h paper_sim PASS 전략보다 실전에서 유리한 이유 (논문/사례)

### ⚠️ 주의 사항 (Cycle 350)

- **4h paper_sim 기본 max_hold이 24봉으로 변경됨** (Cycle 349 E, `ACTIVE_TIMEFRAME=="4h"` 시 자동)
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **SOL 합성 데이터 보정 시**: HIGH% 40% 이하 목표, vol_spike_prob 0.35→0.25

### 핵심 메트릭 (Cycle 349 확정)

| 지표 | Cycle 348 | Cycle 349 | 변화 |
|------|-----------|-----------|------|
| price_cluster 1h Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster 1h Consistency | 1/8 | **1/8** | 유지 |
| price_cluster 4h Sharpe (max_hold=24) | - | **2.26** | ✅ 신규 |
| supertrend_multi 4h Sharpe (max_hold=24) | - | **2.20** | ✅ 신규 |
| cmf 4h Sharpe (max_hold=24) | - | **0.84** | ✅ 신규 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| ETH dema_cross High% | 80.8% | **80.8%** | 유지 (구조적 원인 확정) |
| 1h PASS 수 | 0/20 (28연속) | **0/20 (29연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS OFI Sharpe | 4.345 | **4.345** | 유지 |

### Cycle 349 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `--max-hold-override` CLI 인자 추가 |
| `scripts/paper_simulation.py` | 4h 기본 max_hold: 24봉(4일) 자동 설정 (1h는 48봉 유지) |

### Cycle 348 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `scripts/generate_garch_csv.py` | sigma clip 10x→4x, vol_spike 2.5x→1.5x, wick cap base_vol*3 추가 |
| `data/historical/synthetic/ETHUSDT/1h.csv` | 재생성 (HL ratio 4.30%→2.12%) |
| `data/historical/synthetic/SOLUSDT/1h.csv` | 재생성 (HL ratio 동일 수준, vol 특성상 잔존) |

### Cycle 347 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/manager.py` | evaluate()에 RANGING 레짐 시 ema50_slope→set_ranging_macro_neutral() 자동 연동 추가 |
| `tests/test_risk_manager.py` | _make_candle_df_with_ema_slope() 헬퍼 + TestRangingMacroNeutralManagerIntegration 4개 테스트 추가 |

### F(리서치) BTC 1h 레짐별 특성 (Cycle 346 확정)

| 레짐 | 캔들 비율 | avg return/봉 | ema50 slope mean | 중립(<0.0005) 비율 |
|------|---------|------------|----------------|----------------|
| TREND_UP | 31.3% | +0.0250% | +0.001391 | 14.4% |
| TREND_DOWN | 21.4% | +0.0377% | -0.001266 | 18.9% |
| RANGING | 47.3% | +0.0217% | +0.000110 | 45.1% |

**핵심 결론**: RANGING에서만 neutral macro 비율 45.1% 확보 → mean-reversion 조건 충족

### ETH 합성 데이터 슬리피지 레짐 (Cycle 348 확정)

| 데이터 | HL ratio mean | ATR14/close | HIGH regime(>=3%) |
|--------|-------------|-------------|------------------|
| BTC real | 1.50% | 1.49% | 0.7% |
| ETH synthetic (old) | 4.30% | 4.33% | 39.3% |
| ETH synthetic (new) | 2.12% | 2.12% | 21.0% |
| SOL synthetic (new) | 4.12% | 4.13% | 54.0% |

### EMA slope 차단 비율 분석 (Cycle 346 D(ML) 확정)

| ema_slope_min_buy 임계값 | 전체 BUY pass | RANGING BUY pass | 판단 |
|------------------------|-------------|----------------|------|
| 0.0 (필터 없음) | 54.7% | 50.8% | 기본값 |
| 0.0005 | 44.3% | 38.2% | ✅ 중간 균형점 |
| 0.001 | 34.5% | 27.1% | ⚠️ RANGING 과도 차단 |
| 0.002 | ~25% | ~20% | ❌ 지나치게 엄격 (제거됨) |

### E(실행) 슬리피지 진단 결과 (Cycle 344 확정)

| 지표 | BTC 1h 전체 평균 |
|------|----------------|
| HIGH 레짐 비율 | 0~8% (최대 dema_cross 8.3%) |
| 동적 슬리피지 조정 필요성 | **없음** |

### Bundle OOS avg_oos_mdd (Cycle 346 확정, 변화 없음)

| 전략 | avg_oos_mdd |
|------|-------------|
| cmf | 5.2% |
| order_flow_imbalance_v2 | 3.4% |
| supertrend_multi | 2.2% |
| vwap_cross | 2.7% |
| value_area | 1.9% |

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

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상 (Cycle 348 재생성)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only for timing)
