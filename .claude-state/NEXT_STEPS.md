# Next Steps

_Last updated: 2026-06-27 (Cycle 360 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 360

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 358 | C+B+F | price_cluster bounce_pct=0.020 악화 확인→0.010 복원, cooldown_active 주석 보완, dema_cross dist_pct 0.001→0.002(SharpeStd 2.69→2.32 ✓) |
| 359 | D+E+F | ATR필터(dead param for BTC), RSI방향성필터코드추가(미테스트), PaperConnector use_tiered 노출, n_bins=6 악화→n_bins=5복원 |
| 360 | A+C+F | dema_cross rsi_dir_filter=True 검증(PF 1.26→1.45↑, trades 31→18↓), close_window=40 악화→기본값(50)복원, Bundle OOS 5/5 PASS 유지 |

### 🎯 Cycle 361 작업 방향 (361 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor 안정성 개선

- **배경**: Cycle 357에서 직렬화 버그 수정 완료, cooldown_active 주석 보완 완료
- **작업**:
  - CircuitBreaker 룰 재검토 — 현재 기준이 과도한지/부족한지 확인
  - VaR/CVaR 계산 로직 검증 (`src/risk/` 확인)
  - Kelly Sizer 파라미터 현황 확인 (과도한 레버리지 방지)

#### D(ML): dema_cross WFO 실행 또는 앙상블 가중치 검토

- **배경**: Cycle 360 A에서 rsi_dir_filter=True 확정 (PF 1.45, Sharpe 0.40)
  - dema_cross: trades 18 (avg), 2개 윈도우 trades=14<15 경계치 주의
  - PF=1.45 (PASS 기준 1.5까지 +0.05)
- **작업 방향**:
  - Option A: rsi_dir_filter=True로 dema_cross WFO 직접 실행하여 최적 fast/slow 확인
  - Option B: 앙상블 RF 모델 피처 중요도 분석 (현재 어떤 피처가 주도?)

#### F(리서치): roc_ma_cross 분석 (1h BTC rank1)

- **배경**: Cycle 360 paper_sim에서 roc_ma_cross rank1 (Sharpe=0.34, SharpeStd=2.44, 2/8 consistency)
  - 2/8 consistency → 가장 일관된 PASS 후보 중 하나
  - FAIL 원인: sharpe 0.02<1.0 (x1), PF 1.02<1.5 (x1), mc_p_value 0.485>0.1
- **작업**: roc_ma_cross 파라미터 검토 및 개선 가능성 분석
  - DEFAULT_GRIDS["roc_ma_cross"] 현황 확인 (roc_period=[10,12,15], ma_period=[3,5,7])

### ⚠️ 주의 사항 (Cycle 361)

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

### 핵심 메트릭 (Cycle 360 업데이트)

| 지표 | Cycle 359 | Cycle 360 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Trades | 31 | **18** | rsi_dir_filter=True 적용 (-13) |
| 1h BTC dema_cross Sharpe | 0.37 | **0.40** | ↑+0.03 개선 |
| 1h BTC dema_cross PF | 1.26 | **1.45** | ↑+0.19 개선 (목표 1.5까지 +0.05) |
| 1h BTC dema_cross SharpeStd | 2.32 | **2.25** | ↑ 안정화 |
| 1h BTC price_cluster Sharpe | 0.72 | **0.72** | 복원 (close_window=40 악화→default(50) 복원) |
| 1h PASS 수 | 0/19 (42연속) | **0/19 (43연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

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
