# Next Steps

_Last updated: 2026-06-24 (Cycle 353 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 353

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 351 | B+D+F | min_trades_override 추가, 4h min_trades 15→8 완화, 통계 근거 확인 |
| 352 | B+D+F | supertrend_multi atr_threshold=0.5 적용, DrawdownMonitor 절댓값 ATR% 필터 추가 |
| 353 | C+E+F | wick_reversal 1h 제외, dema_cross fast=8/slow=20 실험→롤백, engulfing_zone 크로스심볼 분석 |

### 🎯 Cycle 354 작업 방향 (354 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): price_cluster BTC 1h Sharpe 개선 — ML 기반 파라미터 최적화

- **배경**: price_cluster 3사이클 연속 BTC rank=1 (Sharpe=0.87, return=+4.99%)
  - Sharpe=0.87 (기준 1.0 미달 0.13 차이), PF=1.20 (기준 1.5 미달)
  - 가장 PASS에 근접한 전략이나 Sharpe/PF 모두 미달
- **작업**:
  - `src/strategy/price_cluster.py` 분석: 어떤 파라미터가 Sharpe를 제한하는지 확인
  - BTC 1h 데이터에서 최적 클러스터 반경/수 조사
  - `PAPER_SIM_STRATEGY_PARAMS`에 price_cluster 파라미터 실험 (실제 결과 확인 필수)
  - 단, BTC real data 개선이 먼저 → 합성 ETH/SOL 개선은 부수적

#### E(실행): dema_cross 대안 접근 — 거리 기반 신호 검토

- **배경**: dema_cross 파라미터 조정 실험 결과
  - fast=8/slow=20: BTC 5 trades, ETH 8 trades, SOL 13 trades → 여전히 15 미달
  - ETH Sharpe 1.12→0.00 (파라미터 조정 시 역효과)
  - DEMA cross 자체가 너무 드문 이벤트 (주 1회 미만)
- **작업**:
  - dema_cross 대신 "DEMA 거리/경사도" 신호 검토 (크로스 이외 조건 추가)
  - 예: DEMA_fast와 DEMA_slow 간격이 임계값 이하로 좁아질 때 예비 신호 → 진입 증가
  - 단, 전략 파일 수정이므로 backtest/walk_forward.py에서 검증 필수
  - **주의**: 전략 파일 직접 수정 가능 (버그 픽스 성격), 단 실제 BTC 1h 검증 필수

#### F(리서치): price_cluster 왜 BTC에서만 작동하는가

- **배경**: price_cluster BTC rank=1 (+4.99%) vs ETH rank=4 (-0.31%) vs SOL rank=19(-8.27%)
  - BTC real: 클러스터 패턴이 실제 지지/저항으로 기능
  - ETH/SOL synthetic: 클러스터 의미 없음 (GARCH 과정에는 가격 메모리 없음)
- **작업**:
  - price_cluster 전략 로직 분석 (클러스터 계산 방식)
  - BTC real 데이터에서 클러스터 분포 확인 (가격 집중 구간)
  - ETH/SOL synthetic 데이터에서 클러스터 분포 비교
  - 결론: price_cluster가 BTC 전용 전략인지, 아니면 실제 ETH/SOL 데이터에서도 통할지

### ⚠️ 주의 사항 (Cycle 354)

- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
  - BTC 1h -9.31% + ETH/SOL 0 trades x8 → 구조적 실패. 4h 테스트는 미확인
- **dema_cross 기본 파라미터 유지** (fast=10, slow=25): 파라미터 조정 실험 실패로 롤백
  - 대안 접근 필요: 크로스 감지 방식 자체를 바꾸거나 진입 주기를 다른 방식으로 증가
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 353 확정)

| 지표 | Cycle 352 | Cycle 353 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 20개 | **19개** | wick_reversal 제외 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| 1h BTC roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH engulfing_zone Consistency | 2/8 | **2/8** | 유지 |
| 1h ETH dema_cross Sharpe | 1.12 | **0.00** | fast=8/slow=20→롤백 |
| 1h PASS 수 | 0/20 (32연속) | **0/19 (33연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

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
