# Next Steps

_Last updated: 2026-06-15 (Cycle 314 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 314

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 312 | B+D+F | kelly_fraction_multiplier 테스트 추가(4개), nr_lookback=4 실험→효과없음(복원), TRAIN_HOURS=84일 실험→역효과(210일 복원) |
| 313 | C+B+F | NR_SCAN_WINDOW=5 실험→역효과(PF=0.90, std=5.447) 확정 후 3 복원, should_kill_strategy 레짐별 테스트 추가(9개) |
| 314 | D+E+F | vol_spike_mult 파라미터화(non-filter 확인), live_paper_trader --timeframe 추가, cmf 4h PASS 확인 |

### 🎯 Cycle 315 작업 방향 (315 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): narrow_range ATR_THRESHOLD 0.95→1.05 실험
- **Cycle 314 D(ML) 결론**: vol_spike_mult는 신호 필터가 아님 (confidence 결정에만 사용)
  - trades [8,10,10,9,10]는 VOL_SPIKE_MULT 변경과 무관
  - **진짜 binding constraint**: ATR_THRESHOLD=0.95 (NR 봉의 ATR이 평균의 95% 미만이어야 함)
- **다음 실험**: `ATR_THRESHOLD` 0.95→1.05 (ATR 축소 조건 거의 폐기 수준으로 완화)
  - 기대: fold0(8 trades), fold3(9 trades) → 10+ 으로 개선 → 저거래 제외 해소
  - 위험: 고변동성 구간에서도 NR 신호 발생 → 오신호 증가, avg OOS 악화 가능
  - 방법: `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]["atr_threshold"] = 1.05` 추가
    단, NarrowRangeStrategy에 `atr_threshold` init param 추가 필요 (현재 클래스 상수만)

#### C(데이터): cmf 4h PASS 검증 및 활용
- **Cycle 314 Bundle OOS 결과**: cmf 5/5 PASS (avg=2.508, PF=1.387) — 신규 PASS
  - 주의: min_wfe=0.4 완화 기준 사용 (fold2 WFE=0.434, fold3 WFE=0.449 < 0.5)
  - fold2/fold3는 표준 min_wfe=0.5 기준이면 FAIL
  - **검토 필요**: 완화 기준(0.4)이 적절한지, 아니면 cmf 파라미터 개선으로 WFE 개선 가능한지
- **C 작업**: cmf 전략 4h 파라미터 검토
  - 현재 PAPER_SIM_STRATEGY_PARAMS["cmf"] = {"buy_thresh": 0.10}
  - 현재 BUNDLE_STRATEGY_OVERRIDES["cmf"] = {"min_wfe": 0.4, "sharpe_decay_max": 0.40}
  - 실전 투입 전 WFE 완화 기준 제거 가능성 검토 (표준 0.5로 강화 후 결과 확인)

#### F(리서치): supertrend_multi + cmf 4h 실전 투입 검토
- **두 전략 모두 Bundle OOS PASS**: supertrend_multi(avg=3.674, PF=2.475), cmf(avg=2.508, PF=1.387)
- **실전 투입 준비**: `python3 scripts/live_paper_trader.py --timeframe 4h` 가능 (Cycle 314 E에서 구현)
  - 단, live_paper_trader는 Bybit API 연결 필요 (SSL 차단 환경에서 불가)
  - **대안**: paper_simulation.py --timeframe 4h 실행으로 4h walk-forward 시뮬 가능
- **F 작업**: cmf 4h paper_simulation 결과 분석
  - `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --symbols BTC/USDT` 실행
  - supertrend_multi 4h와 cmf 4h 비교

### ⚠️ 주의 사항 (Cycle 315)
- **narrow_range ATR_THRESHOLD**: 현재 0.95 (클래스 상수) — init 파라미터 추가 후 실험
  - `NarrowRangeStrategy.__init__()` 에 `atr_threshold: float = 0.95` 파라미터 추가 (vol_spike_mult처럼)
  - `generate()` 에서 `self.ATR_THRESHOLD` → `self.atr_threshold` 변경
  - BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]["atr_threshold"] = 1.05 추가
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가
- **NR_SCAN_WINDOW**: 현재 3 (복원됨) — 변경 금지
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 314 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - `cmf: {"buy_thresh": 0.10}` ← Cycle 309 D
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 314 복원):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← vol_spike_mult 실험 종료 복원
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}` ← 유지
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (변경 없음)
- **Bundle OOS 실행 시 `--csv-dir data/historical` 필수** (5-fold 구조, 2023~2024 실제 BTC)
- **live_paper_trader.py**: 이제 `--timeframe 4h` 지원 (Cycle 314 E에서 추가)

### 핵심 메트릭 (Cycle 314)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일): **0/22 PASS**
  - rank1: price_cluster (Sharpe=0.59, 3/8, PF=1.18)
  - rank2: supertrend_multi (Sharpe=0.32, 2/8, PF=1.14)
  - narrow_range (vol_spike_mult=1.0 기본): rank15, Sharpe=-1.42, PF=0.90 (변동 없음)
  - 주 실패 원인: PF < 1.5 (구조적 문제 지속)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **2/5 PASS**
  - **cmf: 5/5 PASS** (avg=2.508, PF=1.387) — 신규 (relaxed WFE=0.4 기준)
  - **supertrend_multi: 3/5 PASS** (avg=3.674, PF=2.475) — 지속 PASS
  - narrow_range: avg=-1.927, std=3.480 → FAIL (vol_spike_mult는 필터 아님 확인)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7-10분 소요 (BTC 기준)
