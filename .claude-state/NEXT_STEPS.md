# Next Steps

_Last updated: 2026-06-26 (Cycle 357 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 357

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 355 | A+C+F | vol_atr_trend_min 1.5→1.2 강화, WFO 그리드 확장, dema_cross 거리필터 0.5%→0.1% 완화 |
| 356 | B+D+F | DrawdownMonitor 검증(정상), dema_cross fast=8/slow=20(trades 3→50!), price_cluster 1.0 실험→악화→1.2복원 |
| 357 | B+D+F | DrawdownMonitor to_dict 4개 필드 누락 수정, dema_cross RSI 70→65(Sharpe 0.37→0.47), price_cluster vol_regime_filter=False 실험(동일 Sharpe=0.87 → 필터 무관 확인) |

### 🎯 Cycle 358 작업 방향 (358 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): price_cluster PF 1.20→1.5+ 개선 방안 탐색

- **배경**: Cycle 357 F에서 vol_regime_filter True/False 모두 Sharpe=0.87, PF=1.20 동일 확인
  - **결론**: vol_regime_filter 자체는 bottleneck이 아님. PF<1.5가 구조적 문제
- **작업**:
  - `src/strategy/price_cluster.py` 분석: 손실 거래 패턴 확인 (특히 PF가 낮은 window 분석)
  - bounce_pct 조정 실험: 현재 [0.010, 0.020, 0.025] → 0.010 이하(0.005) 시도 여부 평가
  - 거래 방향(BUY/SELL) 분리 분석: 어느 방향에서 손실이 발생하는지 확인

#### B(리스크): CircuitBreaker 룰 검토

- **배경**: DrawdownMonitor to_dict/from_dict 수정 완료 (Cycle 357 B)
- **작업**:
  - `src/risk/circuit_breaker.py` 존재 여부 확인 및 DrawdownMonitor 연동 검토
  - DriftMonitor 상태도 직렬화 여부 확인 (동일 누락 패턴 가능성)

#### F(리서치): dema_cross PF 1.40→1.5+ 개선 방안 탐색

- **배경**: Cycle 357 D에서 RSI 70→65 실험 → Sharpe 0.37→0.47 소폭 개선, PF=1.40 여전히 FAIL
- **작업**:
  - `src/strategy/dema_cross.py` dist_pct 0.001→0.002 실험 (너무 약한 cross 차단)
    - 근거: RSI 필터보다 신호 품질 기준(cross 강도) 강화가 PF 개선에 유리할 수 있음
  - dist_pct=0.002 결과: trades 감소 가능 → trades≥15 기준 충족 여부 확인 필요
  - 또는: 이익실현 조건(max_hold 단축) 실험 → 더 빠른 청산으로 PF 개선

### ⚠️ 주의 사항 (Cycle 358)

- **dema_cross fast=8/slow=20, RSI≤65 확정** (Cycle 357 D): `PAPER_SIM_STRATEGY_PARAMS["dema_cross"]` 유지
  - Sharpe 0.47, SharpeStd=2.69 (여전히 불안정), PF=1.40 (bottleneck)
  - 다음 실험: dist_pct 0.001→0.002로 신호 품질 강화
- **price_cluster vol_regime_filter=False** (Cycle 357 F): `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` 유지
  - True/False 모두 Sharpe=0.87, PF=1.20 동일 → vol_regime_filter 파라미터 무관 확인
  - 완전 제거 검토: 다음 cycle에서 vol_regime_filter 파라미터 제거 고려
- **walk_forward DEFAULT_GRIDS["price_cluster"] vol_regime_filter [False, True] 추가됨** (Cycle 357 F)
- **DrawdownMonitor to_dict()/from_dict() 4개 필드 수정됨** (Cycle 357 B): ATR/Sharpe/RANGING 상태 복원
- **wick_reversal 1h 제외 확정** (Cycle 353 C): `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 추가됨
- **min_trades_override=8 (4h)**: `engine.min_trades` 1h=15, 4h=8
- **supertrend_multi atr_threshold=0.5**: paper_sim `PAPER_SIM_STRATEGY_PARAMS`에 반영
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지

### 핵심 메트릭 (Cycle 357 확정)

| 지표 | Cycle 356 | Cycle 357 | 변화 |
|------|-----------|-----------|------|
| 1h 테스트 전략 수 | 19개 | **19개** | 유지 |
| 1h BTC dema_cross Trades | 50 | **48** | 소폭 감소 (RSI≤65 필터) |
| 1h BTC dema_cross Sharpe | 0.37 | **0.47** | ⬆️ 소폭 개선 |
| 1h BTC dema_cross SharpeStd | 2.61 | **2.69** | ▼ 소폭 악화 (불안정 지속) |
| 1h BTC dema_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h BTC price_cluster Sharpe | -0.30 (1.0→복원) | **0.87 (vol_filter=False)** | vol_filter 무관 확인 |
| 1h PASS 수 | 0/19 (36연속) | **0/19 (38연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 357 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/drawdown_monitor.py` | `to_dict()` 4개 누락 필드 추가: `_atr_vol_elevated`, `_atr_vol_mult`, `_sharpe_decay_mult`, `_ranging_macro_neutral` (Cycle357 B) |
| `src/risk/drawdown_monitor.py` | `from_dict()` 4개 상태 복원 추가 (Cycle357 B) |
| `src/risk/drawdown_monitor.py` | `DrawdownStatus.cooldown_active` 필드 문서화 (Cycle357 B) |
| `src/strategy/dema_cross.py` | RSI BUY 필터 70→65 강화 (Cycle357 D) |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` vol_regime_filter=False 비활성화 실험 (Cycle357 F) |
| `src/backtest/walk_forward.py` | `DEFAULT_GRIDS["price_cluster"]` vol_regime_filter [True]→[False, True] (Cycle357 F) |

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

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 357 업데이트)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← 1h paper_sim에서 제외됨
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`
- `supertrend_multi: {"atr_threshold": 0.5}` ← Cycle 352 B 추가
- `price_cluster: {"vol_regime_filter": False}` ← **Cycle 357 F**: filter=False 실험(True와 동일 Sharpe=0.87)
- `dema_cross: {"fast": 8, "slow": 20}` ← Cycle 356 D 추가 (3 trades → 50 trades!)

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
