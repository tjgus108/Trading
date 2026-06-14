# Next Steps

_Last updated: 2026-06-14 (Cycle 310 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 310

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 308 | C+B+F | CMFStrategy warmup 버그 수정(period 기반 min_rows), DrawdownMonitor WARN 히스테리시스 추가 |
| 309 | D+E+F | cmf buy_thresh=0.10 paper_sim 실험(미미한 개선), 슬리피지 레짐 추적 추가, NR ema_slope 조사 |
| 310 | A+C+F | cmf period=40 역효과 확인(복원), NR ema_slope_min_buy/max_sell 구현, bundle OOS init params 업데이트 |

### 🎯 Cycle 311 작업 방향 (311 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor 및 Kelly Sizer 점검
- **슬리피지 레짐 리포트 추가 (Cycle 310 F 미완성)**:
  - `scripts/paper_simulation.py` `generate_report()`: 전략별 slippage_regime_counts 컬럼 추가
  - 목적: price_cluster MDD=12.2%에서 high_regime 비율 확인
  - 구현: BacktestEngine result에서 slippage_regime_counts 수집 → 리포트 테이블 추가
  - 주의: BacktestEngine은 adaptive_slippage=True여야 작동

#### D(ML): narrow_range ema_slope 실험 결과 분석
- **Cycle 311 Bundle OOS 실행 후 확인**:
  - BUNDLE_STRATEGY_INIT_PARAMS 업데이트 완료 (Cycle 310): `ema_slope_min_buy=0.001, ema_slope_max_sell=-0.001`
  - 기대: fold3 OOS=-10.794 (2023-12 ~ 2024-02 BTC 불마켓) → ≥0 개선 (SELL 차단 효과)
  - fold1 OOS=-3.828 (2023-08 ~ 2023-10 베어마켓) → ≥0 개선 (BUY 차단 효과)
  - 만약 fold2 OOS=1.540 유지 또는 개선이면 → ema_slope_min_buy=0.001 성공
  - 실험 후 결과를 DEFAULT_GRIDS로 피드백

#### F(리서치): 슬리피지 레짐 + 1h vs 4h 전략 차별화 분석
- **1h 전체 FAIL 근본 원인 탐구** (Cycle 310 A 결론 기반):
  - cmf 1h FAIL: period 무관, 구조적 bar quality 문제
  - 가설: 1h paper_sim의 0/22 PASS는 walk-forward 윈도우 설정 문제일 수 있음
  - 대안 탐구: TRAIN_HOURS 변경 (5040h→2016h), TEST_HOURS 변경 (1440h→720h)
  - 근거: 현재 train=210일, test=60일 → 실전 HFT 기준으로는 train 과도할 수 있음

### ⚠️ 주의 사항 (Cycle 311)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 310 변경):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - **`cmf: {"buy_thresh": 0.10}` ← Cycle 310 A: period=40 역효과 확인 후 period=20(기본값) 복원**
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 310 변경):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.001, "ema_slope_max_sell": -0.001}` ← Cycle310 C(데이터)
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **feed.py ema20_slope 추가** (Cycle 310 C):
  - `df["ema20_slope"] = df["ema20"].diff() / df["ema20"]` — 단위: 상대변화율
  - NarrowRangeStrategy: `ema_slope_min_buy=0.0, ema_slope_max_sell=0.0` (기본=필터없음)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 310)
- 테스트: **8400 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster: rank1 score=75.7 (안정, 3/8 consistent, MDD=12.2%)
  - supertrend_multi: rank2 score=68.3 (2/8 consistent)
  - cmf: rank19 score=낮음 Sharpe=-2.33 (period=40 역효과, period=20 복원)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)
  - cmf 5/5 ALL PASS (avg OOS Sharpe=2.508, std=1.888)
  - narrow_range fold3 OOS=-10.794 지속 (ema_slope 필터 다음 OOS에서 효과 확인 예정)
  - value_area OOS std=2.018 (임계값 0.018 초과 FAIL 지속)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 7-10분 소요
