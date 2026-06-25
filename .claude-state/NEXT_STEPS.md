# Next Steps

_Last updated: 2026-06-25 (Cycle 354 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 354

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 352 | B+D+F | supertrend_multi atr_threshold=0.5 적용, DrawdownMonitor 절댓값 ATR% 필터 추가 |
| 353 | C+E+F | wick_reversal 1h 제외, dema_cross fast=8/slow=20 실험→롤백, engulfing_zone 크로스심볼 분석 |
| 354 | D+E+F | price_cluster vol_regime_filter 실험→효과없음, dema_cross narrowing→역효과→롤백, price_cluster real/synthetic 차이 분석 |

### 🎯 Cycle 355 작업 방향 (355 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): price_cluster Sharpe 개선 — n_bins/bounce_pct 파라미터 조정

- **배경**: price_cluster 4사이클 연속 BTC rank=1 (Sharpe=0.87, return=+4.99%)
  - vol_regime_filter=True 효과 없음 (Cycle 354 D): ATR/ATR_MA > 1.5 구간 희박
  - 시도 안 한 파라미터: n_bins (5→4), bounce_pct (0.01→0.008)
- **작업**:
  - n_bins=4 실험: 클러스터 폭 넓혀 더 많은 가격이 하나의 클러스터에 포함 → bounce 조건 완화
  - bounce_pct=0.008 실험: 진입 조건 좁히기 → 신호 정밀도 향상
  - 단, 실제 BTC 데이터 결과 확인 필수

#### C(데이터): roc_ma_cross 분석 — 일관성 2/8에서 개선 방안

- **배경**: roc_ma_cross BTC 1h Consistency 2/8 (rank=2, Sharpe=0.34)
  - 2사이클 연속 2/8 (최고 일관성이지만 50% 미달)
  - FAIL 원인: 일부 window mc_p_value > 0.1 (우연 가능성), sharpe < 1.0
- **작업**:
  - `src/strategy/roc_ma_cross.py` 분석: ROC 기간, MA 기간 확인
  - BTC 1h에서 어떤 window에서 PASS하고 어떤 window에서 FAIL하는지 확인
  - 파라미터 조정 여지 탐색 (단, 실제 BTC 데이터 검증 필수)

#### F(리서치): dema_cross narrowing의 올바른 방향 재설계

- **배경**: Cycle 354 E 실험 실패 — narrowing 신호가 역방향이었음
  - fast>slow AND narrowing → BUY(틀림): 하향 크로스 임박이므로 SELL이 맞음
  - fast<slow AND narrowing → SELL(틀림): 상향 크로스 임박이므로 BUY가 맞음
- **재설계 방향**:
  - Option A: "역추세 narrowing" — fast>slow AND narrowing → SELL (크로스 전 단기 역추세)
  - Option B: "확산 기반" — fast>slow AND gap 확대 → BUY (추세 강화 신호)
  - BTC 1h Consistency 분석 후 방향 결정

### ⚠️ 주의 사항 (Cycle 355)

- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **dema_cross 기본 파라미터 유지** (fast=10, slow=25): narrowing 실험 실패, 재설계 필요
  - **narrowing 방향 오류 확인** (Cycle 354 E): fast>slow AND narrowing → BUY X, SELL O
- **price_cluster vol_regime_filter 비효과 확인** (Cycle 354 D): BTC 1h 데이터에서 ATR/ATR_MA > 1.5 희박
  - n_bins, bounce_pct 조정 실험으로 전환 (다음 A 사이클에서)
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 354 확정)

| 지표 | Cycle 353 | Cycle 354 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 (vol_filter 효과 없음) |
| 1h BTC roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH dema_cross Sharpe | 0.00 | **0.00** | 유지 (narrowing→롤백) |
| 1h PASS 수 | 0/19 (33연속) | **0/19 (34연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 354 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=True 실험 → 효과 없음 → 롤백 |
| `src/strategy/dema_cross.py` | narrowing 조건 추가 실험 → 역효과 → 롤백 |

### Cycle 353 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가 |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 353 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가

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
