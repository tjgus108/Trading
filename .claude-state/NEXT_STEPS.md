# Next Steps

_Last updated: 2026-06-15 (Cycle 314 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 314

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 312 | B+D+F | kelly_fraction_multiplier 테스트 추가(4개), nr_lookback=4 실험→효과없음(복원), TRAIN_HOURS=84일 실험→역효과(210일 복원) |
| 313 | C+B+F | NR_SCAN_WINDOW=5 실험→역효과(PF=0.90, std=5.447) 확정 후 3 복원, should_kill_strategy 레짐별 테스트 추가(9개) |
| 314 | D+E+F | VOL_SPIKE_MULT 0.5 실험→역효과(avg=-1.927) 복원, --csv-dir 기본값 고정→**2/5 PASS**, supertrend_multi 4h params 구조 개선 |

### 🎯 Cycle 315 작업 방향 (315 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): cmf 4h 실전 투입 준비
- **Cycle 314 Bundle OOS 핵심 결과**: cmf **PASS** (5/5, avg Sharpe=2.508, PF=1.387)
  - 5-fold 모두 통과 — 가장 안정적인 전략 (std=1.888)
  - **실전 투입 후보 #2**: cmf 4h가 supertrend_multi와 함께 유망
- **A 작업**: cmf 4h 파라미터 검토
  - cmf fold 상세: fold[0]~fold[4] 모두 OOS Sharpe 양수 (0.642~5.111)
  - `BUNDLE_STRATEGY_INIT_PARAMS["cmf"]`: 현재 overrides={"min_wfe": 0.4, "sharpe_decay_max": 0.40}
  - cmf init params 현황 확인 (`src/strategy/cmf.py`)
  - `PAPER_SIM_STRATEGY_PARAMS_4H`에 cmf 4h 최적 파라미터 추가 검토
  - 테스트 커버리지 확인 및 필요시 보강

#### C(데이터): narrow_range 구조적 분석 (강세장 오신호)
- **Cycle 314 D(ML) 결론**: VOL_SPIKE_MULT는 binding constraint 아님 확정
  - 실험: vol_spike_mult=0.5 → trades 증가 미미, avg OOS=-1.927 (FAIL)
  - fold[3] (2023-12~2024-02 강세장): OOS=-11.387 구조적 FAIL
    - IS=-0.021 (근사 0) → 학습 불가 구간 → OOS 신뢰 불가
    - 2023-12~2024-02: BTC 강세장 시작 ($42K→$52K) → NR 전략 SHORT 오신호 폭발
- **C 작업**: narrow_range 강세장 대응 분석
  - `vol_spike_mult` init 파라미터화 완료 (Cycle 314) — 추가 실험 가능
  - 다음 후보 실험: `ATR_THRESHOLD` 완화 (0.95→1.05) 단독 실험
    - 기대: ATR 필터 통과율 증가 (더 많은 신호 → trades 증가)
    - 위험: 고변동성 구간에서 오신호 증가 가능
  - 대안: bull 레짐 SELL 억제 (`ema_filter=True`) 추가 검토
    - EMA200 위에서 SHORT 차단 → 강세장 오신호 감소

#### F(리서치): cmf 4h vs 1h 구조 비교
- **Cycle 314 F 핵심 성과**: --csv-dir 기본값 고정으로 5-fold 안정화
  - cmf 4h: 5/5 PASS (avg Sharpe=2.508) vs cmf 1h: 0/8 PASS (avg Sharpe=-1.21)
  - 동일 전략이 타임프레임에 따라 극명한 성능 차이 → 1h 노이즈 문제 재확인
- **가설**: cmf 4h가 1h에서 실패하는 구조적 원인
  - 1h: CMF 신호가 too noisy → buy_thresh=0.10도 충분하지 않음
  - 4h: 충분한 볼륨 집계 → CMF 신호 신뢰도 ↑
  - **검토**: cmf 1h에서 period=40 역효과(Cycle 310) 원인 재분석
    - period 증가 → 더 긴 볼륨 평균 → 최근 이벤트 희석 → 신호 지연

### ⚠️ 주의 사항 (Cycle 315)
- **NR_SCAN_WINDOW**: 현재 3 (변경 금지)
- **vol_spike_mult**: 현재 1.0 (클래스 상수, init 파라미터화 완료) — 실험 역효과 확정, 변경 금지
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 314 추가: PAPER_SIM_STRATEGY_PARAMS_4H):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - `cmf: {"buy_thresh": 0.10}` ← Cycle 309 D
  - **4H 전용** (`PAPER_SIM_STRATEGY_PARAMS_4H`): `supertrend_multi: {atr_threshold=0.5, ...}` ← Cycle 314 E
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정**:
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← Cycle 311 (vol_spike_mult 실험 후 복원)
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (변경 없음)
- **Bundle OOS 기본값**: `--csv-dir data/historical` (Cycle 314 F에서 고정됨) → 5-fold 보장
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 314)
- 테스트: **8413 passed, 23 skipped** (회귀 없음, vol_spike_mult init 파라미터 추가 후 테스트 통과)
- Paper Sim BTC 1h (8 windows, TRAIN=210일): **0/22 PASS** (변화 없음)
  - rank1: price_cluster (Sharpe=0.59, 3/8, PF=1.18)
  - rank2: supertrend_multi (Sharpe=0.02, 2/8, PF=1.06, MDD=9.0%)
  - 주 실패 원인: PF < 1.5 (구조적 문제 지속)
- **Bundle OOS BTC 4h (5-fold, --csv-dir=data/historical): 2/5 PASS** ← Cycle 314 핵심 성과
  - cmf: **PASS** (5/5, avg Sharpe=2.508, PF=1.387, trades=17/fold)
  - supertrend_multi: **PASS** (avg Sharpe=3.674, PF=2.475)
  - narrow_range: FAIL (vol_spike_mult=0.5 역효과: std=3.480, avg=-1.927)
  - elder_impulse: FAIL (std=3.117, avg=-2.941)
  - value_area: FAIL (std=2.018, avg=0.713)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 기본값으로 고정됨 (Cycle 314 F) → 5-fold 4h 구조
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7-10분 소요 (BTC 기준)
