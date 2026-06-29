# Next Steps

_Last updated: 2026-06-29 (Cycle 366 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 366

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 364 | D+E+F | dema_cross fast=7 역효과 확정(PF1.45→1.00, Sharpe0.40→-0.69)→fast=8 복원, optimize_frama atr_period 버그 수정, PaperConnector 슬리피지 단위 명문화 |
| 365 | A+C+F | fast=8 복원 확인(Sharpe=0.40, PF=1.45, Trades=18), rsi_dir_threshold 파라미터화(45/50), optimize_dema_cross() 함수 추가(DEFAULT_GRIDS 활성화) |
| 366 | B+D+F | DrawdownMonitor 시나리오 테스트(88→90 테스트), threshold=45 확인(Sharpe0.40→0.55, Trades18→26, PF1.45→1.35), slow=25 사전 분석(33.1/60d) |

### 🎯 Cycle 367 작업 방향 (367 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): KellySizer 현황 점검

- Cycle362 B에서 kelly_cap > max_fraction 시 debug 로그 추가 완료
- **작업**: KellySizer 실데이터 시나리오 테스트 (BTC 1h 기준 파라미터 적정성 검증)
  - kelly_fraction, max_fraction 파라미터 실효성 확인
  - DrawdownMonitor kelly_fraction_multiplier 연동 동작 검증

#### D(ML): dema_cross slow=25 실험 검토

- **배경**: Cycle366 D(ML)에서 threshold=45 → Sharpe 0.55, PF 1.35, rank2 확정
  - slow=25+thr=45 신호 33.1/60d (충분), 현재 PF 1.35 < 목표 1.50
  - slow=25가 DEMA 간격 확장 → 더 강한 추세 신호 → PF 회복 가능성?
- **작업**:
  - paper_simulation.py에서 slow=25 실험 설정 (fast=8, slow=25, thr=45)
  - paper_sim 실행 후 PF 변화 관찰 (slow=20/thr=45의 1.35 대비)
  - slow=25가 PF 1.35→1.40+ 달성 여부 확인
  - 악화 시: roc_ma_cross PF=1.22 개선 탐색 전환

#### F(리서치): roc_ma_cross PF 개선 가능성 탐색

- **배경**: roc_ma_cross rank3, Sharpe=0.34, PF=1.22 — 이미 안정적이나 PF 부족
  - ema_span 또는 roc_period 조정으로 PF 1.22→1.30+ 가능한지 분석
  - NEXT_STEPS: dema_cross 실험 한계 도달 시 대안 전략 개선 검토
- **탐색**: 신호 빈도 분석 (현재 36/60d avg) + PF 방향 추정

### ⚠️ 주의 사항 (Cycle 367 이후)

- **dema_cross threshold=45 확정** (Cycle366 D): Sharpe 0.55, PF 1.35, Trades 26, rank2
  - fast=7 패턴(PF 1.45→1.00) 아님 — PF 소폭 하락(1.45→1.35) 허용 가능
  - Cycle367 D(ML)에서 slow=25 실험 → PF 회복 여부 확인
- **optimize_dema_cross() 함수 추가됨** (Cycle365 C): DEFAULT_GRIDS 활성화
  - rsi_dir_threshold=[45,50] 그리드 포함 → WFO 탐색 가능
  - test_optimize_dema_cross_helper 테스트 추가됨 (Cycle366 D)
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

### 핵심 메트릭 (Cycle 366 업데이트)

| 지표 | Cycle 365 | Cycle 366 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Sharpe | 0.40 (thr=50) | **0.55 (thr=45)** | +0.15 ↑↑ |
| 1h BTC dema_cross PF | 1.45 (thr=50) | **1.35 (thr=45)** | -0.10 mild↓ (허용) |
| 1h BTC dema_cross Trades | 18 | **26** | +8 ↑↑ |
| 1h BTC dema_cross Rank | 5/19 | **2/19** | rank5→2 ✅ |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 (rank1) |
| 1h BTC price_cluster SharpeStd | 1.10 | **1.10** | 안정성 우수 ✓ |
| 1h BTC roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 (rank3) |
| 1h BTC frama Sharpe | 0.24 | **0.24** | 유지 (rank4) |
| 1h PASS 수 | 0/19 (49연속) | **0/19 (50연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| 테스트 수 | 8434 | **8436** | +2 새 테스트 |

### Cycle 366 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `tests/test_drawdown_monitor.py` | 일중 DD 회복 → WARNING 자동 해제 테스트 추가 (Cycle366 B) |
| `tests/test_drawdown_monitor.py` | 주간 DD HALT 유지/reset_weekly() 해제 테스트 추가 (Cycle366 B) |
| `tests/test_phase_d.py` | `test_optimize_dema_cross_helper` 테스트 추가 (Cycle366 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] 주석 업데이트: Cycle366 threshold=45 결과 반영 (Cycle366 D) |

### Cycle 365 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/strategy/dema_cross.py` | `rsi_dir_threshold=50` 파라미터 추가 — BUY/SELL RSI 임계값 가변화 (Cycle365 A) |
| `src/backtest/walk_forward.py` | `optimize_dema_cross()` 함수 추가 — DEFAULT_GRIDS["dema_cross"] 활성화 (Cycle365 C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"]에 `rsi_dir_threshold=[45,50]` 추가 (Cycle365 A/C) |
| `scripts/paper_simulation.py` | dema_cross `rsi_dir_threshold=45` 실험 설정 (Cycle366 D 검증 완료) |

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
