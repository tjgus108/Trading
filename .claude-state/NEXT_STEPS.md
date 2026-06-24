# Next Steps

_Last updated: 2026-06-24 (Cycle 352 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 352

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 350 | A+C+F | SOL HIGH% 54%→39% 수정, 4h 슬리피지 버그 수정, price_cluster Bundle OOS 불가 확정 |
| 351 | B+D+F | min_trades_override 추가, 4h min_trades 15→8 완화, 통계 근거 확인 |
| 352 | B+D+F | supertrend_multi atr_threshold=0.5 적용, DrawdownMonitor 절댓값 ATR% 필터 추가 |

### 🎯 Cycle 353 작업 방향 (353 mod 5 = 3 → C(데이터) + E(실행) + F(리서치))

#### C(데이터): wick_reversal ETH/SOL 1h 0 trades 문제 조사 및 수정

- **배경**: Cycle 352 1h sim 결과
  - wick_reversal: ETH 8/8 window 0 trades, SOL 8/8 window 0 trades
  - BTC에서도 wick_reversal 성과 불량 (return=-9.31% worst in BTC)
  - 원인 후보: 합성 데이터의 고가/저가 분포가 wick 패턴을 생성하지 않음
- **작업**:
  - `src/strategy/wick_reversal.py` 신호 조건 분석
  - ETH/SOL 합성 데이터에서 wick 패턴 발생 빈도 확인
  - 수정 방향: 진입 조건 완화 OR 1h 시뮬레이션 제외 목록 추가 (value_area, supertrend_multi처럼)

#### E(실행): dema_cross ETH 1h trades 부족 분석 — 진입 조건 최적화

- **배경**: Cycle 352 ETH 1h — dema_cross Sharpe=1.12 (>1.0!) but trades=6 (<15)
  - Sharpe 기준은 통과하지만 trades 부족으로 FAIL (consistency 0/8)
  - trades만 늘리면 PASS 가능성 있는 가장 근접한 전략
- **작업**:
  - dema_cross ETH 1h에서 trades 6건밖에 없는 이유 분석
  - `src/strategy/dema_cross.py` 진입 조건 확인
  - 파라미터 조정으로 trades 증가 검토 (e.g. period 단축, threshold 완화)
  - 단, 합성 데이터에서만 개선 시 적용 금지 — BTC 1h에서도 검증 필수

#### F(리서치): engulfing_zone 크로스심볼 일관성 분석

- **배경**: Cycle 352 1h 결과 — engulfing_zone이 ETH/SOL에서 top 1 (return +3.50%, +4.81%)
  - BTC는 순위권 밖, ETH 2/8 consistency, SOL 1/8
  - ETH 최고 성과 전략인데 BTC에서 왜 미순위?
- **작업**:
  - engulfing_zone BTC 1h FAIL 원인 상세 분석 (어느 window에서 어떤 이유로 실패?)
  - ETH/SOL에서 좋은 이유와 BTC에서 나쁜 이유의 구조적 차이 파악
  - engulfing 패턴이 BTC vs ETH/SOL 데이터에서 다르게 나타나는지 확인

### ⚠️ 주의 사항 (Cycle 353)

- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영 (Cycle 352 B)
- **DrawdownMonitor.set_atr_state() 시그니처 변경** (Cycle 352 D): `atr_pct`, `atr_pct_threshold` 파라미터 추가
  - 하위호환: 기본값 `atr_pct=0.0` (비활성) → 기존 호출자 영향 없음
- **4h 슬리피지 버그 수정 완료** (Cycle 350 A): BTC 4h HIGH%=0% 정상화 유지
- **SOL 1h HIGH% 극단적**: dema_cross=85.5%, frama=52.5% → SOL 1h 고변동성 레짐 주의
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 352 확정)

| 지표 | Cycle 351 | Cycle 352 | 변화 |
|------|-----------|-----------|------|
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| 1h BTC price_cluster SharpeStd | — | **1.10** | 최안정 확인 |
| 1h BTC roc_ma_cross Consistency | — | **2/8** | 최고 일관성 |
| 1h ETH engulfing_zone Consistency | — | **2/8** | ETH 최고 |
| 1h ETH dema_cross Sharpe | — | **1.12** | trades=6로 FAIL |
| 1h SOL dema_cross HIGH% | — | **85.5%** | 극고변동성 확인 |
| 1h PASS 수 | 0/20 (31연속) | **0/20 (32연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| supertrend_multi atr_threshold | 0.7 (기본) | **0.5** (paper_sim 4h) | ✅ no-trades 해결 |

### Cycle 351 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/engine.py` | `min_trades_override` 파라미터 추가, `run()`에서 `self.min_trades` 사용 |
| `scripts/paper_simulation.py` | `min_trades_override=8 if 4h else 0` 엔진에 전달, 리포트 기준 동적 표시 |

### Cycle 350 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `scripts/generate_garch_csv.py` | SOL vol_spike_prob: 0.35→0.15 |
| `data/historical/synthetic/SOLUSDT/1h.csv` | 재생성 (HIGH% 54%→39%) |
| `scripts/paper_simulation.py` | BacktestEngine에 `timeframe=ACTIVE_TIMEFRAME` 추가 (슬리피지 버그 수정) |

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
