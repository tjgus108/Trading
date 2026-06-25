# Next Steps

_Last updated: 2026-06-25 (Cycle 354 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 354

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 352 | B+D+F | supertrend_multi atr_threshold=0.5 적용, DrawdownMonitor 절댓값 ATR% 필터 추가 |
| 353 | C+E+F | wick_reversal 1h 제외, dema_cross fast=8/slow=20 실험→롤백, engulfing_zone 크로스심볼 분석 |
| 354 | D+E+F | walk_forward price_cluster grid 버그 수정, vol_regime_filter 실험 추가, convergence_signal BTC 검증 실패 |

### 🎯 Cycle 355 작업 방향 (355 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): price_cluster vol_regime_filter 실험 결과 평가

- **배경**: Cycle 354에서 `PAPER_SIM_STRATEGY_PARAMS["price_cluster"] = {"vol_regime_filter": True, "vol_atr_trend_min": 1.5}` 추가
  - 목적: BTC Sharpe 0.87→1.0+, PF 1.20→1.5+ 개선 시도
  - 예상 메커니즘: ATR/ATR_MA > 1.5이면 추세장 → 신호 억제 → trending 구간 false signal 제거
- **작업**:
  - paper_sim 재실행 후 price_cluster 결과 비교 (filter 적용 전: Sharpe=0.87, PF=1.20)
  - 효과 있으면: vol_atr_trend_min 범위 탐색 (1.5, 2.0, 2.5 비교)
  - 효과 없으면: vol_regime_filter=True 제거하고 다른 방향 탐색

#### C(데이터): 신호 빈도 분석 — price_cluster vs roc_ma_cross 비교

- **배경**: BTC rank=1/2 두 전략 모두 Sharpe 미달
  - price_cluster: Sharpe=0.87 (0.13 미달), PF=1.20 (PF 미달이 더 큰 문제)
  - roc_ma_cross: 2/8 consistency (가장 높은 일관성) but Sharpe=0.34
- **작업**:
  - price_cluster PF=1.20인 이유 분석: 승률 37.2% vs 필요 수준 확인
  - roc_ma_cross가 2/8 consistent한 윈도우 기간 분석 (어떤 시장 환경에서 PASS?)
  - 두 전략의 신호 겹침 분석: 동시 BUY/SELL 시 포트폴리오 상관관계

#### F(리서치): dema_cross 대안 — 완전히 다른 전략 로직 검토

- **배경**: Cycle 354 E 결론 — convergence 접근은 BTC에서 치명적 실패
  - 23 trades(baseline) vs 867 trades(convergence) → Sharpe -2.37, -76% 손실
  - dema_cross 기본 크로스 방식 자체도 BTC에서 Sharpe=-2.08, 3 trades (거의 동작 안 함)
- **작업**:
  - dema_cross를 포기하고 같은 slots(1h paper_sim 19개 전략)에서 더 나은 전략 후보 탐색
  - 단 **새 전략 파일 생성 금지** — 기존 355개 중 미테스트 전략 중 후보 탐색
  - 또는 dema_cross 거리 필터 0.5% → 0.1%로 완화 (현재 필터가 cross 신호도 차단 가능성)

### ⚠️ 주의 사항 (Cycle 355)

- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
  - BTC 1h -9.31% + ETH/SOL 0 trades x8 → 구조적 실패. 4h 테스트는 미확인
- **dema_cross convergence_signal 접근 FAIL** (Cycle 354 E): BTC -76% (-2.37 Sharpe) 검증 완료
  - convergence_signal 파라미터는 dema_cross.py에 보존(기본값 False) — ETH real data용
  - 다음 방향: dema_cross 거리 필터 완화 또는 다른 전략으로 교체 검토
- **price_cluster vol_regime_filter=True 실험 중** (Cycle 354 D): paper_sim에 추가됨
  - 다음 사이클에 시뮬 결과 평가 필수
- **walk_forward price_cluster 그리드 개선** (Cycle 354 D): vol_regime_filter=[True] 추가
  - 기존 vol_atr_trend_min이 dead parameter였던 버그 수정
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 354 확정)

| 지표 | Cycle 353 | Cycle 354 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 (vol_filter 실험 준비) |
| 1h BTC roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH engulfing_zone Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH dema_cross Sharpe | 0.00 | **1.12** | 기본파라미터 복원 (전사이클 롤백) |
| 1h PASS 수 | 0/19 (33연속) | **0/19 (34연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 354 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]`에 `"vol_regime_filter": [True]` 추가 (dead parameter 버그 수정) |
| `src/strategy/dema_cross.py` | `convergence_signal=False`, `convergence_threshold=0.02` 파라미터 추가 (기본값 False, 실험용) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"] = {"vol_regime_filter": True, "vol_atr_trend_min": 1.5}` 추가 |

### Cycle 353 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가 |

### Cycle 352 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `"supertrend_multi": {"atr_threshold": 0.5}` 추가 |
| `src/risk/drawdown_monitor.py` | `set_atr_state()` atr_pct 절댓값 임계값 확장 |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 354 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": True, "vol_atr_trend_min": 1.5}` ← Cycle 354 D 추가 (실험)

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
