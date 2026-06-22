# Next Steps

_Last updated: 2026-06-22 (Cycle 345 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 345

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 343 | C+B+F | BTC CSV 품질확인, RANGING kill 1.5→1.2, avg_oos_mdd 추가, 0/20 23연속 |
| 344 | D+E+F | BundleOOSResult.avg_oos_mdd 필드화, SlipH% window진단, 슬리피지 무관 확인, 0/20 24연속 |
| 345 | A+C+F | WFO그리드 vol_regime_filter 버그수정, ema20_slope 동기화, ccxt타이밍버그수정, 0/20 25연속 |

### 🎯 Cycle 346 작업 방향 (346 mod 5 = 1 → B(리스크) + D(ML) + F)

#### B(리스크): RANGING 환경 리스크 파라미터 재검토

- **배경**: Cycle 343에서 RANGING kill multiplier 1.5→1.2로 강화. 25연속 0/20
  - RANGING에서 position sizing 더 줄이는 방향 검토
  - WFO grid에 vol_regime_filter=True 추가 효과: 다음 시뮬에서 확인 예정
- **작업**:
  - `src/risk/manager.py` RANGING 레짐 처리 코드 재검토
  - RANGING에서 Kelly 계수 추가 감소 or 포지션 완전 중단 옵션 검토
  - `tests/test_risk.py` 회귀 확인

#### D(ML): price_cluster vol_regime_filter 효과 검증

- **배경**: Cycle 345 A(품질)에서 WFO 그리드 수정 (vol_regime_filter=True 추가)
  - 기존: vol_atr_trend_min이 vol_regime_filter=False로 무효화 → 54조합 모두 동일
  - 수정: vol_regime_filter=True 고정, 실제 레짐 필터 활성화
- **작업**:
  - 다음 paper_simulation.py 실행 시 price_cluster 결과 주목
  - vol_regime_filter=True에서 거래 수(AvgTrades)가 41에서 얼마나 줄어드는지 확인
  - Sharpe std 1.10이 줄어드는지 (W5/W6 분산 감소) 확인

#### F(리서치): frama 전략 분석

- **배경**: frama가 BTC 1h에서 rank3(Sharpe=0.24, PF=1.12, 1/8 consistency)
  - FRAMA (Fractal Adaptive Moving Average): 시장 변동성에 적응하는 MA
  - 현재 WFO 그리드: period=[14,16,18], rsi_period=[12,14,16]
- **작업**:
  - `src/strategy/frama.py` 전략 로직 확인
  - WFO 그리드에 추가 파라미터 탐색 가능성 (signal_thresh 등)
  - 4h frama 성능 vs 1h frama 비교 (bundle OOS에 추가 가능성)

### ⚠️ 주의 사항 (Cycle 346)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: Cycle 344 확인 → HIGH% < 1%, 동적 조정 불필요
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 345 확정)

| 지표 | Cycle 344 | Cycle 345 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h PASS 수 | 0/20 (24연속) | **0/20 (25연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS avg_mdd | 5.2%/4.9%/3.1%/2.4%/2.9% | **5.2%/3.4%/2.2%/2.7%/1.9%** | OFI/ST/VA 개선 |

### Cycle 345 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | price_cluster WFO 그리드에 vol_regime_filter=[True] 추가 (vol_atr_trend_min 실효화 버그 수정) |
| `tests/test_exchange.py` | ccxt 설치 타이밍 버그 수정 — if not HAS_CCXT 제거, connector 동적 교체 보장 |
| `scripts/paper_simulation.py` | enrich_indicators()에 ema20_slope 추가 (feed.py 동기화) |

### E(실행) 슬리피지 진단 결과 (Cycle 344 확정)

| 지표 | BTC 1h 전체 평균 |
|------|----------------|
| LOW 레짐 비율 | 0% (모든 전략) |
| NORMAL 레짐 비율 | 92~100% |
| HIGH 레짐 비율 | 0~8% (최대 dema_cross 8.3%) |
| W5 vol=1.39% → 레짐 | NORMAL (0.5~3% 범위) |
| 동적 슬리피지 조정 필요성 | **없음** — HIGH%가 무시할 수준 |

### IS/OOS 레짐 진단 결과 (Cycle 340 신규, 유지)

| Window | IS end-state | OOS dominant | mkt | price_cluster | roc_ma_cross |
|--------|-------------|--------------|-----|---------------|--------------|
| W1 | TREND_UP | TREND_UP | bull | -1.43 FAIL | 4.04 PASS |
| W2 | TREND_UP | RANGING | bull | 0.11 FAIL | 3.84 PASS |
| W3 | RANGING | RANGING | bear | 0.00 FAIL | -0.04 FAIL |
| W4 | RANGING | RANGING | bear | -0.41 FAIL | -2.01 FAIL |
| W5 | RANGING | RANGING | sideways | 0.99 FAIL | -3.77 FAIL |
| W6 | RANGING | RANGING | sideways | **3.78 PASS** | -0.28 FAIL |
| W7 | RANGING | RANGING | bull | -0.08 FAIL | -1.12 FAIL |
| W8 | TREND_UP | RANGING | bull | 0.21 FAIL | -2.05 FAIL |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only)

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
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |
