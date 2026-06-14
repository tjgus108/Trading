# Next Steps

_Last updated: 2026-06-14 (Cycle 309 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 309

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 307 | B+D+F | tiered halt roundtrip 테스트 추가, atr_trend_max=1.1 효과 없음 확정, cmf_1h 임계값 강화 |
| 308 | C+B+F | CMFStrategy warmup 버그 수정(period 기반 min_rows), DrawdownMonitor WARN 히스테리시스 추가 |
| 309 | D+E+F | cmf buy_thresh=0.10 paper_sim 실험(미미한 개선), 슬리피지 레짐 추적 추가, NR ema_slope 조사 |

### 🎯 Cycle 310 작업 방향 (310 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 테스트 커버리지 및 전략 품질 점검
- **cmf 1h vs 4h 성능 격차 분석 (Cycle 309 진단)**:
  - 4h: 5/5 PASS avg Sharpe=2.508 (period=21≈84h lookback)
  - 1h: rank14 Sharpe=-1.21 (period=20=20h lookback) → 4h 대비 lookback이 4배 짧음
  - **핵심 가설**: 1h cmf가 노이즈에 취약 → 4h 등가 lookback(period=80-84) 실험 필요
  - 실험: `PAPER_SIM_STRATEGY_PARAMS["cmf"] = {"period": 40, "buy_thresh": 0.10}` (단독 실험)
    - 근거: period=40×1h = 40h (4h period=10의 등가) — 중간 단계부터 탐색
    - 또는 period=80 (4h period=20 등가) — 직접 등가 테스트

#### C(데이터): NarrowRangeStrategy ema_slope_min 지원 추가
- **Cycle 309 F(리서치) 결론**: NarrowRangeStrategy에 ema_slope_min 미지원
  - `ema_slope_min` 파라미터 없음, `enrich_indicators()`에 ema20_slope 컬럼도 없음
  - 구현 계획 (C(데이터) 태스크):
    1. `src/data/feed.py` `_add_indicators()`: `df["ema20_slope"] = df["ema20"].diff() / df["ema20"]` 추가
    2. `src/strategy/narrow_range.py`: `ema_slope_min: float = 0.0` 파라미터 추가
       - `generate()` 진입 전: `ema_slope = df["ema20_slope"].iloc[curr_idx]` → `< ema_slope_min`이면 HOLD
       - 주의: 음수 slope (하락추세) 에서 BUY 차단 (fold1,3 베어마켓 손실 방지)
       - 주의: 양수 slope (상승추세) 에서 SELL 차단 (fold3 BTC 불마켓 손실 방지)
    3. `src/backtest/walk_forward.py`: `DEFAULT_GRIDS["narrow_range"]`에 추가:
       - `"ema_slope_min_buy": [0.0, 0.001, 0.002]` — BUY 조건: EMA slope ≥ N%
       - `"ema_slope_max_sell": [0.0, -0.001, -0.002]` — SELL 조건: EMA slope ≤ N%
  - **단독 실험**: ema_slope 파라미터만 추가, nr_lookback은 고정

#### F(리서치): 슬리피지 레짐 추적 활용 분석
- **Cycle 309 E(실행) 결과**: `slippage_regime_counts` 추가됨
  - 다음 사이클 시뮬 후 price_cluster와 cmf의 레짐 분포 비교 분석
  - price_cluster MDD=12.2% — high regime 비율이 높으면 슬리피지가 핵심 원인
  - **확인 방법**: paper_simulation.py 결과에서 slippage_regime_counts 로그 확인
  - (현재 paper_sim은 BacktestEngine 결과를 레포트에 포함하지 않음 → 추가 검토 필요)

### ⚠️ 주의 사항 (Cycle 310)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 309 변경):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - **`cmf: {"buy_thresh": 0.10}` ← Cycle 309 D(ML) 신규 추가** (기존 rank15→14, 효과 미미)
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (변경 없음):
  - `narrow_range: {"trend_regime_filter": True, "atr_trend_max": 1.1}` ← 효과 없음 확정
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **BacktestEngine 변경 (Cycle 309)**:
  - `BacktestResult.slippage_regime_counts: Dict[str, int]` 추가 (기본 빈 dict)
  - adaptive_slippage=True 시 진입마다 low/normal/high 카운트
  - `summary()`에서 출력됨
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 309)
- 테스트: **8400 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster: rank1 score=75.7 (안정)
  - supertrend_multi: rank2 score=68.3 (안정)
  - cmf: rank14 score=50.0 Sharpe=-1.21 trades=72 (buy_thresh=0.10 미미한 개선)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)
  - cmf 5/5 ALL PASS (avg OOS Sharpe=2.508, std=1.888)
  - narrow_range fold3 OOS=-10.794 지속 (EMA slope 필터 구현 필요)
  - value_area OOS std=2.018 (임계값 0.018 초과 FAIL 지속)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 7-10분 소요
