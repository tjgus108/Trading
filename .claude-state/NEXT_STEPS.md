# Next Steps

_Last updated: 2026-06-26 (Cycle 357 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 357

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 355 | A+C+F | vol_atr_trend_min 1.5→1.2 강화, WFO 그리드 확장, dema_cross 거리필터 0.5%→0.1% 완화 |
| 356 | B+D+F | DrawdownMonitor 검증(정상), dema_cross fast=8/slow=20(trades 3→50!), price_cluster 1.0 실험→악화→1.2복원 |
| 357 | B+D+F | DrawdownMonitor 직렬화 버그 수정(5개 필드), RSI65 효과없음 확인, vol_filter=False 실험(BTC dead param 확인) |

### 🎯 Cycle 358 작업 방향 (358 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): price_cluster vol_regime_filter 결론 및 bounce_pct 탐색

- **배경**: Cycle 357 F에서 vol_regime_filter=False 실험 → BTC 1h에서 dead parameter 확인
  - BTC 1h ATR/ATR_MA 거의 항상 1.2 미만 → filter=True/False 동일 결과
  - vol_regime_filter는 BTC 1h에서는 불필요한 파라미터
- **작업**:
  - `scripts/paper_simulation.py` PAPER_SIM_STRATEGY_PARAMS["price_cluster"]:
    - vol_regime_filter=False 유지 (현재) — dead param 확인되어 변경할 이유 없음
    - 대신 bounce_pct 조정 탐색: 현재 기본값 0.01, paper_sim에서 명시 설정 없음
    - `{"vol_regime_filter": False, "bounce_pct": 0.01}` → Sharpe 0.87 원인 분석
  - 근본 원인 분석: price_cluster PF=1.20 (< 1.5 기준) 원인
    - FAIL 이유: `sharpe 0.91 < 1.0 (x2)`, `profit_factor 0.93 < 1.5 (x1)` → PF가 주원인
    - n_bins=5/bounce_pct=0.01 조합의 신호 품질 문제 → 다른 조합 시도

#### B(리스크): DrawdownStatus.cooldown_active 문서화

- **배경**: Cycle 357 B에서 직렬화 버그 수정 완료 (5개 필드 추가)
- **작업**:
  - `DrawdownStatus.cooldown_active`는 single loss cooldown만 반영 (streak cooldown 제외)
  - 라이브 모니터링에서 streak cooldown 여부 확인 방법: `DrawdownMonitor.is_in_streak_cooldown()` 직접 호출
  - 이슈 없음 (의도적 설계) → 문서화 주석만 추가 검토

#### F(리서치): dema_cross noise 감소 방법 탐색

- **배경**: RSI 65 강화 (Cycle 357 D) 효과 없음 → 다른 방법 탐색
- **확인된 사실**:
  - BTC 1h DEMA 크로스 이벤트에서 RSI 65-70 구간 해당 거래 없음 (RSI 필터 무력)
  - SharpeStd=2.69 (불안정, std > 2.5 위험 수준)
- **작업**:
  - dist_pct 0.001→0.002 (약간 상향) 실험: 너무 약한 cross 차단 → noise 감소 기대
  - `src/strategy/dema_cross.py`: `if dist_pct < 0.001:` → `if dist_pct < 0.002:`
  - 예상 효과: trades 48 → 30~40 (일부 노이즈 cross 차단), Sharpe 안정성 향상 기대

### ⚠️ 주의 사항 (Cycle 358)

- **dema_cross fast=8/slow=20 확정** (Cycle 356 D): `PAPER_SIM_STRATEGY_PARAMS["dema_cross"]` 유지
  - ETH 고슬리피지(37.3%) 주의: BTC 위주로 평가
  - SharpeStd=2.69 → dist_pct 0.001→0.002 실험으로 noise 감소 시도 (Cycle 358 F)
  - RSI 65 강화(Cycle 357 D) 효과 없음 확인 — DEMA 크로스 이벤트와 RSI 65-70 무관
- **price_cluster vol_regime_filter=False 확정** (Cycle 357 F): dead parameter 확인
  - BTC 1h ATR/ATR_MA 항상 1.2 미만 → filter 효과 없음 → False로 고정
  - Sharpe=0.87 개선 위해 bounce_pct 조정 탐색 예정 (Cycle 358 C)
- **DrawdownMonitor 직렬화 수정** (Cycle 357 B): 5개 필드 누락 수정
  - `_atr_vol_elevated`, `_atr_vol_mult`, `_sharpe_decay_mult`, `_current_regime`, `_ranging_macro_neutral`
  - `transition_cushion_enabled/threshold` from_dict 복원 추가
- **walk_forward DEFAULT_GRIDS["dema_cross"] 추가됨** (Cycle 356 D): [8,10,12] x [15,20,25]
- **walk_forward DEFAULT_GRIDS["price_cluster"] vol_regime_filter=[False,True] 추가** (Cycle 357 F)
- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 357 확정)

| 지표 | Cycle 356 | Cycle 357 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Trades | 50 | **48** | 유지 (RSI65 효과없음) |
| 1h BTC dema_cross Sharpe | 0.37 | **0.47** | ⬆️ 소폭 개선 |
| 1h BTC dema_cross SharpeStd | 2.61 | **2.69** | 불안정 유지 |
| 1h BTC price_cluster Sharpe | 0.87 | **0.87** | 유지 (filter=False 효과없음) |
| 1h PASS 수 | 0/19 (36연속) | **0/19 (38연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 356 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": True, "vol_atr_trend_min": 1.2}` ← Cycle 356 F 1.0→복원
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
