# Next Steps

_Last updated: 2026-06-24 (Cycle 352 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 352

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 349 | D+E+F | 4h max_hold=24 우세 확인, --max-hold-override 추가, dema_cross HIGH% 원인 확정 |
| 350 | A+C+F | SOL HIGH% 54%→39% 수정, 4h 슬리피지 버그 수정 (timeframe 미전달), price_cluster Bundle OOS 불가 확정 |
| 351 | B+D+F | min_trades_override 파라미터 추가, 4h min_trades 15→8 완화, 통계 근거 확인 |
| 352 | B+D+F | supertrend_multi no-trades 근본 원인 확정 (Supertrend divergence), SOL HIGH% 개선 (46.4%→10위 밖) |

### 🎯 Cycle 353 작업 방향 (353 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): ETH/SOL 합성 데이터 품질 재검토

- **배경**: ETH 4h avg HIGH%=7-15%, SOL 4h avg HIGH%=24% — synthetic data가 실제 데이터보다 과도하게 volatile
  - ETH/SOL은 synthetic CSV 사용 중 (SSL 차단으로 실데이터 불가)
  - HIGH% 과도한 전략들 (dema_cross SOL 59%, lob_maker SOL 48%): 슬리피지 비용이 Sharpe 음전환 주 원인
- **작업**:
  - ETH 합성 데이터 ATR 분포 확인 (GARCH 파라미터 검토)
  - SOL synthetic vs BTC real ATR 비율 비교 (정상 범위: BTC 1h=1.5%, ETH 2.12%, SOL 3.17%)
  - 합성 데이터 캔들별 vol_spike 집중 여부 분석

#### B(리스크): supertrend_multi min_agree_count 파라미터 추가 (신중하게)

- **배경**: Cycle 352 B 분석 결과
  - no-trades 3개 윈도우(W4,W5,W7): 3개 Supertrend가 단 한 번도 동시 합의 안 됨 (ranging market)
  - ATR 필터는 원인이 아님 (atr_threshold=0.5 변경 → 효과 없음 확인)
  - 현재: `all(t == 1 for t in last_trends)` (3/3 합의 필요)
  - 해결 방향: `min_agree_count` 파라미터 추가 → 2/3 합의로 완화 가능
- **작업**:
  - `src/strategy/supertrend_multi.py`에 `min_agree_count: int = 3` 파라미터 추가
  - `all_bullish = sum(1 for t in last_trends if t==1) >= min_agree_count` 로직 변경
  - **paper_sim에만** `min_agree_count=2` 적용, Bundle OOS는 현재값 유지 (3/3)
  - 효과 측정: no-trades 윈도우 해소 여부, 새 FAIL 원인 발생 여부
  - ⚠️ Bundle OOS 결과 변화 없는지 재확인 필수

#### F(리서치): 4h PASS 전략 구조 분석

- **배경**: 32연속 0/22 PASS → 근본적 접근 재검토 필요
  - BTC 4h supertrend_multi 3/8 (구조적 한계: 3/8 no-trades)
  - 5/8 이상 달성하려면 no-trades 해결 + 현재 FAIL 2개 중 1개 수정 필요
- **작업**:
  - BTC 4h Walk-Forward 윈도우별 시장 레짐 분석 (W4,W5,W7 횡보 비율)
  - Bundle OOS PASS 전략(cmf, ofi_v2, supertrend_multi) 4h paper_sim FAIL 이유 심층 분석
  - Walk-Forward Efficiency(WFE) vs paper_sim consistency 상관관계 계산

### ⚠️ 주의 사항 (Cycle 353)

- **supertrend_multi atr_threshold=0.5 확정** (Cycle 352): PAPER_SIM_STRATEGY_PARAMS에 추가
  - `atr_threshold=0.5`: Bundle OOS와 동일화, ATR 차단 없음 확인
  - `atr_threshold_max=1.5`: SOL HIGH% 개선 (46.4%→top-10 밖), trades 16→13
- **min_trades_override=8 (4h 확정)**: Cycle 351 B에서 BacktestEngine에 추가, paper_sim에 적용
  - `engine.min_trades`: 1h=15, 4h=8
  - 통계 근거: n=8, Sharpe=1.0 → t=2.83, p=0.013 < 0.05
- **4h 슬리피지 버그 수정 완료** (Cycle 350 A): `paper_simulation.py` `timeframe=ACTIVE_TIMEFRAME`
  - BTC 4h HIGH%=0% (정상화 확인)
  - SOL 4h: ATR=5.45% (>6% 비율 24%), 전략별 HIGH%는 신호 집중 특성에 따름
- **SOL vol_spike_prob=0.15 확정** (Cycle 350 C): HIGH% 39.0%
- **4h max_hold=24봉 기본값 유지** (Cycle 349 E)
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 352 확정)

| 지표 | Cycle 351 | Cycle 352 | 변화 |
|------|-----------|-----------|------|
| 4h supertrend_multi BTC Consistency | **3/8** | **3/8** | 변화 없음 (no-trades=Supertrend 불일치) |
| 4h supertrend_multi BTC avg_trades | 8 | 8 | 변화 없음 |
| 4h supertrend_multi SOL avg_trades | 16 | **13** | ↓ (atr_threshold_max=1.5 효과) |
| 4h supertrend_multi SOL Sharpe | -1.92 | **-1.16** | ↑ 개선 (HIGH 진입 감소) |
| SOL supertrend_multi HIGH% 순위 | #3 (46.4%) | **top-10 밖** | ✅ 개선 |
| 1h PASS 수 | 0/20 (31연속) | **0/20 (32연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 352 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["supertrend_multi"] = {"atr_threshold": 0.5, "atr_threshold_max": 1.5}` 추가 |

### Cycle 351 코드 변경 요약 (참고)

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
