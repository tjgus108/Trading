# Next Steps

_Last updated: 2026-06-15 (Cycle 314 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 314

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 312 | B+D+F | kelly_fraction_multiplier 테스트 추가(4개), nr_lookback=4 실험→효과없음(복원), TRAIN_HOURS=84일 실험→역효과(210일 복원) |
| 313 | C+B+F | NR_SCAN_WINDOW=5 실험→역효과(PF=0.90, std=5.447) 확정 후 3 복원, should_kill_strategy 레짐별 테스트 추가(9개) |
| 314 | D+E+F | vol_spike_mult=0.5 실험→역효과(복원), --strategies 필터 추가(E실행), cmf 4h BTC PASS 확인(첫번째!) |

### 🎯 Cycle 315 작업 방향 (315 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): narrow_range ATR_THRESHOLD 실험
- **Cycle 314 D 결론**: vol_spike_mult=0.5 역효과 확인 (trades 동일, fold 4 크게 악화)
  - VOL_SPIKE_MULT, NR_SCAN_WINDOW, nr_lookback 모두 binding constraint 아님 확인됨
  - **남은 마지막 후보**: `ATR_THRESHOLD` 완화 (0.95→1.05)
    - 현재: ATR < 평균*0.95 → NR 확인 (ATR 수축 필요)
    - 완화 시: ATR < 평균*1.05 → ATR 수축 조건 거의 폐기 (평균 이하만 허용)
    - 기대: ATR 필터 통과율 증가 → trades 증가, but 고변동성 구간 오신호 증가 위험
  - **구현**: `NarrowRangeStrategy` ATR_THRESHOLD 파라미터화 → BUNDLE_STRATEGY_INIT_PARAMS 실험
  - **단독 실험 원칙**: vol_spike_mult=1.0(기본), NR_SCAN_WINDOW=3(클래스상수) 고정

#### C(데이터): cmf 4h paper_sim 실행 (새 발견 검증)
- **Cycle 314 F 결론**: cmf 4h BTC Bundle OOS 5/5 PASS (avg OOS Sharpe=2.508) ← 첫 PASS!
  - 2022 bear market 제거 효과 확인 (9-fold vs 5-fold)
  - OOS PF avg=1.387 (다소 낮음), std=1.888 (안정적)
- **C 작업**: cmf 4h paper_sim 단독 실행으로 성능 재확인
  - `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --strategies cmf`
  - cmf 4h 결과: Sharpe, PF, Trades, MDD, Consistency 확인
  - PAPER_SIM_STRATEGY_PARAMS["cmf"] = {"buy_thresh": 0.10} 현재 설정 유지
- **추가 검토**: supertrend_multi 4h 단독 paper_sim 결과 vs Bundle OOS 비교

#### F(리서치): cmf PASS 후속 분석 및 ATR_THRESHOLD 실험 준비
- **Cycle 314 Bundle OOS 주요 발견**:
  - cmf: 5/5 PASS (avg=2.508), supertrend_multi: 3/3 PASS (avg=3.674)
  - 2/5 PASS = 첫 번째 복수 PASS 달성!
- **가설 검토**: cmf fold[2] OOS Sharpe=0.642 (낮음), PF=1.088 (기준 미달)
  - 개별 fold PASS 기준 (WFE, decay 등)과 전략 전체 PASS 기준 분리 확인 필요
  - cmf buy_thresh=0.10 효과 vs 기본값(0.08) 비교 검토
- **다음 실험 우선순위**:
  1. ATR_THRESHOLD 완화 (A 카테고리) — narrow_range 마지막 binding constraint
  2. cmf 4h paper_sim 성능 확인 (C 카테고리)
  3. supertrend_multi + cmf 조합 전략 검토 (둘 다 4h PASS)

### ⚠️ 주의 사항 (Cycle 315)
- **VOL_SPIKE_MULT**: 현재 1.0 (기본값) — 클래스 상수 및 __init__ 기본값 모두 1.0
  - 단, `vol_spike_mult` 파라미터는 유지 (향후 실험 가능, 기본=1.0)
- **NR_SCAN_WINDOW**: 현재 3 (복원됨) — 변경 금지
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 314 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}`
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
  - `relative_volume: {"rvol_buy_sell": 1.2}`
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
  - `order_flow_imbalance_v2: {"trend_span": 20}`
  - `cmf: {"buy_thresh": 0.10}`
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 314 vol_spike_mult=0.5 실험 후 복원):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← vol_spike_mult 제거됨
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (변경 없음)
- **Bundle OOS 실행 시 `--csv-dir data/historical` 필수** (5-fold 4h 구조, 2023~2024 실제 BTC)
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 314)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일, --csv-dir data/historical): **0/22 PASS**
  - rank1: price_cluster (Sharpe=0.59, 3/8, PF=1.18)
  - rank2: supertrend_multi (Sharpe=0.32, 2/8, PF=1.14, return=+5.26%)
  - narrow_range: rank7 (Sharpe=-0.42, 0/8, PF=0.99) — 기본값(1.0) 복원 상태
  - 주 실패 원인: PF < 1.5 (1h BTC 구조적 문제)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **2/5 PASS** ← 첫 복수 PASS!
  - cmf: 5/5 PASS (avg=2.508, std=1.888) ← 첫 PASS!
  - supertrend_multi: 3/3 valid PASS (avg=3.674, std=1.860) ← 재확인
  - narrow_range (vol_spike_mult=0.5 실험): FAIL → 역효과 → 복원
  - elder_impulse: FAIL (std=3.117), value_area: FAIL (std=2.018)
- **실전 투입 우선순위**: supertrend_multi 4h rank1 (avg=3.674), cmf 4h rank2 (avg=2.508)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 5-7분 소요 (BTC 단독)
- Paper simulation 4h: `--timeframe 4h --strategies cmf` 단독 실행 가능 (~1-2분)
