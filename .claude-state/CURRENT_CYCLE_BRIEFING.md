# Current Cycle Briefing

_Cycle 335 | 2026-06-20 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): BacktestEngine 청산 이유 추적 기능 추가

- `src/backtest/engine.py` 개선:
  - `BacktestResult` 필드 추가: `sl_hits: int = 0`, `tp_hits: int = 0`, `max_hold_closes: int = 0`
  - `_check_exit()` 반환값을 4-tuple → 5-tuple로 확장 (`close_reason: 'sl'|'tp'|''`)
  - `run()` 루프에서 SL/TP/MAX_HOLD 각각 카운트 추적
  - `summary()` 에 `close_reasons: sl=N tp=N max_hold=N` 출력 추가
  - 미청산 포지션 최종청산(end-of-data)도 max_hold_closes에 포함

- **핵심 발견**: price_cluster 스모크테스트(500봉 합성데이터)에서:
  - 14거래 중 sl=5, tp=2, max_hold=7 → MAX_HOLD 강제청산 50%
  - TP 도달 전 MAX_HOLD_CANDLES=24 (24h) 강제청산이 PF < 1.5의 주요 원인
  - win/loss ratio가 기대 R:R=2.33보다 낮은 1.71 수준인 이유 설명됨

### C(데이터): 데이터 품질 전수 검증

- BTC 1h CSV (real data):
  - 12000 rows, 2023-01-01~2024-05-14, **갭 0개** (완전 연속)
  - 데이터 연장 불가 (SSL 차단 환경에서 거래소 API 접근 불가)

- ETH/SOL synthetic CSV:
  - ETH: 12000 rows, NaN=0, bad OHLC=0, extreme return=0, zero volume=0
  - SOL: 12000 rows, NaN=0, bad OHLC=0, extreme return=0, zero volume=0
  - 품질 문제 없음 (단, SOL synthetic이 1h 슬리피지 HIGH 100% → 현실 데이터와 괴리)

### F(리서치): OFI v2 imbalance_threshold 탐색 완료

- `order_flow_imbalance_v2.py` 분석:
  - `buy_thresh=0.25`, `sell_thresh=-0.25`가 이미 파라미터화된 imbalance_threshold
  - `imbalance = cum_delta / total_vol` 비율의 임계값
  - 4h Bundle OOS: 기본값으로 avg=4.345 (rank1) — 변경 불필요
  - 1h Paper Sim: OFI rank10 (Sharpe=-0.83) — 4h 대비 1h 성능 열세
- 결론: buy_thresh 파라미터화 완료, 다음 실험 = 1h 특화 0.30/-0.30 탐색

## 시뮬레이션 결과 (Cycle 335)

- **테스트**: 8425 passed, 23 skipped (회귀 없음)

- **Paper Sim BTC 1h (20전략, 8 windows)**: **0/20 PASS** (15사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
  - 주요 FAIL 원인: profit_factor < 1.5 전체

- **Bundle OOS BTC 4h**: **5/5 PASS** ← OFI 파라미터 복원 확인
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907) ← delta_window=10 복원
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (336 mod 5 = 1): B(리스크) + D(ML) + F(리서치)

- **B(리스크)**: MAX_HOLD_CANDLES 영향 분석 — 실데이터 close_reason 분포 측정 후 조정 가능성 검토
- **D(ML)**: OFI v2 buy_thresh=0.30 1h 탐색 (PAPER_SIM_STRATEGY_PARAMS만, Bundle OOS 변경 금지)
- **F(리서치)**: close_reason 기반 PF 분석 + 최적 holding period 리서치
