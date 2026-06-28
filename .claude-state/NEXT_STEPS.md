# Next Steps

_Last updated: 2026-06-28 (Cycle 363 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 363

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 361 | B+D+F | DrawdownMonitor/CB/VaR검토(정상), RF PFI음수피처발견(macd_hist -0.060), roc_ma_cross EMA200조건정리+dead code제거, price_cluster Sharpe 0.87로 상승 |
| 362 | B+D+F | KellySizer kelly_cap dead param 명시(로그), PFI n_repeats 소표본 자동증가(10), price_cluster vol_atr_trend_min dead param 확인 |
| 363 | C+B+F | dema_cross fast=7 실험(신호빈도+37%), CB rapid_decline BTC 실증(window=5 pct=5% 77h당1회 적정), frama atr_period=[10,14,18] DEFAULT_GRIDS 추가 |

### 🎯 Cycle 364 작업 방향 (364 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): dema_cross fast=7 실험 결과 검증

- **배경**: Cycle 363 C에서 paper_sim dema_cross를 fast=7/slow=20으로 변경
  - 분석: fast=7로 31.0/60d (fast=8 대비 +37%) → 경계 윈도우(trades=14) → ~19 예상
  - 리스크: fast DEMA 민감도 증가로 노이즈 증가 시 PF 악화 (현재 PF=1.45)
- **작업**:
  - 새 paper_sim 결과에서 dema_cross trades, PF, Sharpe 변화 확인
  - fast=7에서 PF 유지/향상이면: fast=7 확정, DEFAULT_GRIDS 주석 업데이트
  - fast=7에서 PF 악화(<1.45)이면: fast=8 복원, slow 조정 또는 다른 방법 탐색

#### E(실행): Paper Trading 시뮬레이션 실행 신뢰성 점검

- **배경**: Bundle OOS 5/5 PASS 유지 중이나 1h paper_sim 47연속 FAIL
  - 전략들이 4h OOS에서는 강건하지만 1h에서는 noise 과다 가능성
  - paper_sim의 fee/slippage 모델이 실제 거래 조건과 맞는지 재확인
- **작업**:
  - `src/exchange/paper_connector.py` fee/slippage 모델 재검토
  - 1h 통과 기준(Sharpe≥1.0, PF≥1.5)이 적합한지 검토 — 현재 4h보다 엄격한지 확인

#### F(리서치): frama atr_period 그리드 효과 확인

- **배경**: Cycle 363 F에서 DEFAULT_GRIDS["frama"]에 atr_period=[10,14,18] 추가
  - frama BTC rank3 (Sharpe=0.24, SharpeStd=1.60, PF=1.12) — 안정적이나 PF 낮음
  - atr_period 탐색으로 ATR 수축 필터 최적화 기대
- **작업**:
  - walk_forward 실행 시 frama atr_period 탐색 결과 확인
  - atr_period=10(빠른 반응)이 PF에 미치는 영향 분석

### ⚠️ 주의 사항 (Cycle 364)

- **dema_cross dist_pct=0.002 확정** (Cycle 358 F): SharpeStd 2.69→2.32, trades 48→31
  - 목표(SharpeStd<2.5) 달성. 유지.
  - ETH: Sharpe=-2.07 (합성 데이터 특성상 BTC만 평가)
- **price_cluster n_bins=5, close_window=50 확정** (Cycle 359-360):
  - n_bins=6: Sharpe 0.72→-0.84 악화 (Cycle 359 F)
  - close_window=40: Sharpe 0.72→0.07 악화 (Cycle 360 C) — Cycle303과 동일 결론 재확인
  - bounce_pct=0.010, vol_regime_filter=False, n_bins=5, close_window=50(default) 모두 확정
  - price_cluster 탐색 방향: 추가 파라미터 발굴 필요 (현 설정이 1h BTC 최적)
- **dema_cross rsi_dir_filter=True 확정** (Cycle 360 A):
  - PF 1.26→1.45 (↑+0.19, 1.5 목표까지 +0.05), Sharpe 0.37→0.40 (↑+0.03)
  - Trades 31→18 (-13, avg>15 유지 OK; 단 2윈도우 14<15 경계 주의)
  - `scripts/paper_simulation.py` dema_cross params: `{"fast": 8, "slow": 20, "rsi_dir_filter": True}` 확정
- **dema_cross atr_vol_min_pct 코드 추가** (Cycle 359 D): BTC 1h는 dead param (ATR ~1.49%)
- **DrawdownMonitor 직렬화 수정** (Cycle 357 B): 5개 필드 누락 수정 완료
  - `cooldown_active` 주석 보완 완료 (Cycle 358 B)
- **walk_forward DEFAULT_GRIDS["dema_cross"] 추가됨** (Cycle 356 D): [8,10,12] x [15,20,25]
- **walk_forward DEFAULT_GRIDS["dema_cross"] rsi_dir_filter=[False,True] 추가** (Cycle 359 D)
- **walk_forward DEFAULT_GRIDS["price_cluster"] vol_regime_filter=[False,True] 추가** (Cycle 357 F)
- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 363 업데이트)

| 지표 | Cycle 362 | Cycle 363 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Sharpe | 0.40 | **0.40** | 유지 (fast=7 미적용) |
| 1h BTC dema_cross PF | 1.45 | **1.45** | 유지 |
| 1h BTC dema_cross fast param | 8 | **7 (실험)** | Cycle364에서 검증 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| 1h BTC price_cluster SharpeStd | 1.10 | **1.10** | 안정성 우수 ✓ |
| 1h BTC roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| 1h BTC frama Sharpe | 0.24 | **0.24** | 유지 (rank3) |
| 1h BTC frama SharpeStd | 1.60 | **1.60** | 안정성 우수 ✓ |
| 1h PASS 수 | 0/19 (46연속) | **0/19 (47연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 363 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | dema_cross fast=8→7 (신호빈도 +37%, trades<15 해결 실험) (Cycle363 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] fast=[8,10,12]→[7,8,10,12] (Cycle363 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["frama"] atr_period=[10,14,18] 추가 (Cycle363 F) |
| `src/risk/circuit_breaker.py` | 독스트링+파라미터 주석: BTC 1h 실증 데이터 반영 (window=5 pct=5% 77h당1회) (Cycle363 B) |

### Cycle 362 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/kelly_sizer.py` | `__init__`에 kelly_cap > max_fraction 시 debug 로그 추가 (dead param 명시) (Cycle362 B) |
| `src/ml/trainer.py` | `select_features_pfi()`: X_train < 100행 시 n_repeats=10 자동 증가 (Cycle362 D) |

### Cycle 361 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/roc_ma_cross.py` | EMA200 조건 `"ema50" in df.columns` 제거 (중복 체크), `rsi_val` dead code 제거, bare except → Exception (Cycle361 F) |
| `src/backtest/walk_forward.py` | roc_ma_cross 주석 업데이트: rank1 상태 반영, Cycle361 F 수정 기록 (Cycle361 F) |

### Cycle 360 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | dema_cross `rsi_dir_filter=True` 추가 확정 (PF 1.26→1.45, Sharpe 0.37→0.40) (Cycle360 A) |
| `scripts/paper_simulation.py` | close_window=40 실험 → Sharpe 0.72→0.07 악화 → 기본값(50) 복원 (Cycle360 C) |
| `src/backtest/walk_forward.py` | close_window=40 Cycle360 재확인 악화 주석 추가 (Cycle360 C) |

### Cycle 359 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `atr_vol_min_pct=0.0` 파라미터 추가 (BTC에서 dead param 확인) (Cycle359 D) |
| `src/strategy/dema_cross.py` | `rsi_dir_filter=False` 파라미터 추가 (BUY시RSI>50/SELL시RSI<50) (Cycle359 D) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["dema_cross"]`에 `rsi_dir_filter=[False,True]` 추가 (Cycle359 D) |
| `src/exchange/paper_connector.py` | `use_tiered_slippage=False` 파라미터 노출 → PaperTrader 전달 (Cycle359 E) |
| `scripts/paper_simulation.py` | n_bins=6 실험 → Sharpe 0.72→-0.84 악화 확인 → default(n_bins=5) 복원 (Cycle359 F) |
| `scripts/paper_simulation.py` | atr_vol_min_pct=0.005 실험 → 효과없음 확인 → 제거 (Cycle359 D) |

### Cycle 358 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32 개선, trades 48→31) (Cycle358 F) |
| `src/risk/drawdown_monitor.py` | `cooldown_active` 필드 주석: single loss cooldown만 반영 명확화 (Cycle358 B) |
| `scripts/paper_simulation.py` | bounce_pct=0.020 실험 후 악화 확인 → 기본값(0.010) 복원 (Cycle358 C) |
| `src/backtest/walk_forward.py` | price_cluster bounce_pct=0.020 paper_sim 악화 기록 주석 추가 (Cycle358 C) |

### Cycle 357 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/drawdown_monitor.py` | `to_dict()` 5개 ATR/Sharpe/regime 필드 + transition_cushion 2개 추가 (Cycle357 B) |
| `src/risk/drawdown_monitor.py` | `from_dict()` 동일 필드 복원 + transition_cushion_enabled/threshold 인자 추가 (Cycle357 B) |
| `src/strategy/dema_cross.py` | BUY 차단 RSI 임계값 70→65 (Cycle357 D, 효과없음 확인) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_regime_filter=True,1.2→False (Cycle357 F) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_regime_filter=[False,True] 추가 (Cycle357 F) |

### Cycle 356 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["dema_cross"]` fast=8, slow=20 추가 (Cycle356 D) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_atr_trend_min 1.2→1.0→1.2 복원 (Cycle356 F) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["dema_cross"]` 추가: fast=[8,10,12], slow=[15,20,25] (Cycle356 D) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_atr_trend_min에 1.0 추가 (Cycle356 F) |

### Cycle 355 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_atr_trend_min 1.5→1.2 (Cycle355 A) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_atr_trend_min에 1.2 추가 (Cycle355 A) |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%(0.005)→0.1%(0.001) 완화 (Cycle355 F) |

### Cycle 354 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]`에 `"vol_regime_filter": [True]` 추가 (dead parameter 버그 수정) |
| `src/strategy/dema_cross.py` | `convergence_signal=False`, `convergence_threshold=0.02` 파라미터 추가 (기본값 False, 실험용) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` 추가 (vol_regime_filter=True, 1.5) |

### F(리서치) BTC 1h 레짐별 특성 (Cycle 346 확정)

| 레짐 | 캔들 비율 | avg return/봉 | ema50 slope mean | 중립(<0.0005) 비율 |
|------|---------|------------|----------------|----------------|
| TREND_UP | 31.3% | +0.0250% | +0.001391 | 14.4% |
| TREND_DOWN | 21.4% | +0.0377% | -0.001266 | 18.9% |
| RANGING | 47.3% | +0.0217% | +0.000110 | 45.1% |

**핵심 결론**: RANGING에서만 neutral macro 비율 45.1% 확보 → mean-reversion 조건 충족

### 4h 슬리피지 임계값 (Cycle 351 확인)

| 타임프레임 | LOW 임계값 | NORMAL 임계값 | HIGH 임계값 | BTC 분류 | SOL 분류 |
|-----------|-----------|--------------|-----------|---------|---------|
| 1h | < 0.5% | 0.5~3.0% | >= 3.0% | NORMAL | HIGH(32%) |
| 4h | < 1.0% | 1.0~6.0% | >= 6.0% | NORMAL (3.0%) | NORMAL avg, HIGH 24%캔들 |
| 1d | < 2.5% | 2.5~14.7% | >= 14.7% | — | — |

### min_trades 기준 (Cycle 351 확정)

| 타임프레임 | min_trades | 근거 |
|-----------|-----------|------|
| 1h | 15 | 60일 window, 30일 train, 충분한 신호 |
| 4h | 8 | 60일 window, max_hold=24봉(4일), 이론 최대 15, 실제 8-10; n=8 Sharpe=1.0 → p=0.013 |

### ETH/SOL 합성 데이터 슬리피지 레짐 (Cycle 351 확인)

| 데이터 | HL ratio mean | ATR14/close | HIGH regime |
|--------|-------------|-------------|-------------|
| BTC real 1h | 1.50% | 1.49% | 0.7% (>=3%) |
| ETH synthetic 1h | 2.12% | 2.12% | 21.0% (>=3%) |
| SOL synthetic 1h | 3.17% | ~3.2% | 39.0% (>=3%) |
| SOL synthetic 4h | 5.42% | 5.45% | 24.0% (>=6%) |

### EMA slope 차단 비율 분석 (Cycle 346 D(ML) 확정)

| ema_slope_min_buy 임계값 | 전체 BUY pass | RANGING BUY pass | 판단 |
|------------------------|-------------|----------------|------|
| 0.0 (필터 없음) | 54.7% | 50.8% | 기본값 |
| 0.0005 | 44.3% | 38.2% | ✅ 중간 균형점 |
| 0.001 | 34.5% | 27.1% | ⚠️ RANGING 과도 차단 |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 358 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": False}` ← Cycle 358 C 확정 (bounce_pct=0.020 악화 확인→기본값 0.010)
- `dema_cross: {"fast": 8, "slow": 20}` ← **Cycle 356 D 추가** (3 trades → 50 trades!)

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)

### STRATEGIES_TIMEFRAME_EXCLUDE 현재 설정 (Cycle 353 업데이트)
- `"1h": {"value_area", "supertrend_multi", "wick_reversal"}`
  - value_area: 1h 구조적 실패 (Cycle 325), 4h Bundle PASS
  - supertrend_multi: 1h 구조적 실패 (Cycle 325), 4h Bundle PASS
  - wick_reversal: ETH/SOL 0 trades x8, BTC Sharpe=-2.64 (Cycle 353 C)

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h paper_sim | 24봉 (96시간=4일) | `paper_simulation.py`: `ACTIVE_TIMEFRAME=="4h"` 자동 |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH: synthetic CSV (data/historical/synthetic/ETHUSDT/1h.csv) — NaN 없음, HL ratio 2.12% (Cycle 348 재생성)
- SOL: synthetic CSV (data/historical/synthetic/SOLUSDT/1h.csv) — NaN 없음, HL ratio 3.17% (Cycle 350 재생성)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
  - SSL 차단으로 실거래소 데이터 수집 불가 → 새 Bundle OOS 실행 시 synthetic fallback → 리포트 덮어쓰기 방지
- Paper simulation 4h: 22 전략 × 3 심볼 × 8 windows → 약 5분 소요
