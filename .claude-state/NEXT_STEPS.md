# Next Steps

_Last updated: 2026-06-25 (Cycle 355 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 355

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 353 | C+E+F | wick_reversal 1h 제외, dema_cross fast=8/slow=20 실험→롤백, engulfing_zone 크로스심볼 분석 |
| 354 | D+E+F | walk_forward price_cluster grid 버그 수정, vol_regime_filter 실험 추가, convergence_signal BTC 검증 실패 |
| 355 | A+C+F | vol_atr_trend_min 1.5→1.2 강화, WFO 그리드 확장, dema_cross 거리필터 0.5%→0.1% 완화 |

### 🎯 Cycle 356 작업 방향 (356 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor / RiskManager 현황 점검

- **배경**: Cycle 352에서 DrawdownMonitor atr_pct 절댓값 임계값 확장 (마지막 B 작업)
- **작업**:
  - `src/risk/drawdown_monitor.py` 로직 검증: 연속손실 스케일(75%/50%) 현황 확인
  - paper_sim 결과의 Half/Full 스케일 적용 빈도 분석 (momentum_quality 173/89회 → 과도?)
  - CircuitBreaker 조건 재검토: MDD > 20% 진입 방어 로직 확인

#### D(ML): dema_cross 0.1% 필터 효과 평가

- **배경**: Cycle 355 F에서 거리 필터 0.5%→0.1% 완화 적용됨
- **작업**:
  - paper_sim 재실행 후 dema_cross trades 변화 확인 (목표: 3→10+ trades)
  - BTC Sharpe 변화 모니터링 (0.1% 필터로 noise 증가 가능성 vs 거래 빈도 개선)
  - ETH dema_cross 0/8 consistency → 거래 빈도 개선 시 trades 15 달성 가능 여부

#### F(리서치): price_cluster vol_atr_trend_min=1.2 효과 평가

- **배경**: Cycle 355 A에서 vol_atr_trend_min 1.5→1.2 변경됨
- **작업**:
  - paper_sim 재실행 후 price_cluster 결과 비교
  - vol_atr_trend_min=1.2 효과 있으면: WR/PF 개선 측정 (목표 WR 42.5%)
  - 효과 없으면: vol_regime_filter 방향 재검토 (1.0 시도 또는 완전 제거)

### ⚠️ 주의 사항 (Cycle 356)

- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **dema_cross 거리 필터 0.1%로 완화됨** (Cycle 355 F): 다음 사이클에 효과 평가 필수
  - 너무 많은 noise trade 유입 시 즉시 0.3% 또는 0.5% 복원
- **price_cluster vol_atr_trend_min=1.2 실험 중** (Cycle 355 A): 다음 사이클에 효과 평가
  - 1.5에서 효과 없었으므로 1.2에서도 무효 시 vol_regime_filter 비활성화 검토
- **walk_forward 그리드 확장** (Cycle 355 A): vol_atr_trend_min=[1.2, 1.5, 2.0, 2.5]
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 355 확정)

| 지표 | Cycle 354 | Cycle 355 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 (1.5 효과 없음 → 1.2 실험 중) |
| 1h BTC roc_ma_cross Consistency | 2/8 | **2/8** | 유지 (W1/W2=Jan~May 2023 강추세 구간) |
| 1h ETH engulfing_zone Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH dema_cross Sharpe | 1.12 | **1.12** | 유지 (trades=6, 0/8 FAIL) |
| 1h BTC dema_cross Trades | 3 | **3** | 유지 (0.1% 필터 효과 다음 사이클 평가) |
| 1h PASS 수 | 0/19 (34연속) | **0/19 (35연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 355 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": True, "vol_atr_trend_min": 1.2}` ← Cycle 355 A 변경 (1.5→1.2)

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
