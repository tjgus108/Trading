# Next Steps

_Last updated: 2026-06-16 (Cycle 315 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 315

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 313 | C+B+F | NR_SCAN_WINDOW=5 실험→역효과(PF=0.90, std=5.447) 확정 후 3 복원, should_kill_strategy 레짐별 테스트 추가(9개) |
| 314 | D+E+F | vol_spike_mult=0.5 실험→역효과(복원), --strategies 필터 추가(E실행), cmf 4h BTC PASS 확인(첫번째!) |
| 315 | A+C+F | atr_threshold=1.05 실험→역효과(avg=-2.118, std=3.889, 복원), cmf 4h BTC-특이성 확인(ETH/SOL FAIL) |

### 🎯 Cycle 316 작업 방향 (316 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): narrow_range 번들 교체 전략 평가
- **Cycle 315 A 결론**: narrow_range 모든 파라미터 실험 완료 → 근본 한계 확인
  - NR_SCAN_WINDOW(3), nr_lookback(5), vol_spike_mult(1.0), ema_slope(0.0), atr_threshold(0.95) 모두 최적
  - 4h에서 IS Sharpe 80% 음수 → 전략 자체가 4h에 부적합
- **B 작업**: 번들에서 narrow_range 교체 검토
  - 교체 후보: `price_cluster` (paper_sim rank1, Sharpe=0.59)
  - 단계:
    1. `run_bundle_oos.py` BUNDLE_STRATEGIES에서 narrow_range → price_cluster 교체
    2. Bundle OOS 4h 실행: `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --csv-dir data/historical`
    3. price_cluster 4h 결과 분석 (5-fold OOS Sharpe, std, trades)
  - **결과에 따라**: PASS면 확정, FAIL이면 roc_ma_cross 또는 positional_scaling 시도

#### D(ML): supertrend_multi fold3 개선 검토
- **Cycle 315 F 결론**: supertrend_multi fold3 (2023-12-27~2024-02-24) OOS=-6.308, trades=2 — 저거래 문제
  - 현재: excluded (regime_transition_is_min=2.0 기준으로 제외되어 있지 않음 → FAIL로 처리됨)
  - fold3 is_start=2023-06-30, IS Sharpe=3.842 (높음), WFE=-1.642 → 레짐 전환 마커 아님
  - 저거래(trades=2 < 3) → excluded → 유효 fold=3/5만 집계
- **D 작업**: supertrend_multi fold3 저거래 원인 파악
  - `run_bundle_oos.py` BUNDLE_STRATEGY_OVERRIDES["supertrend_multi"] 현재 min_oos_trades=3
  - fold3 2023-12-27~2024-02-24: BTC가 40k 돌파 구간 — CMF 필터가 과도한 차단?
  - 실험: `cmf_confirm=False`로 임시 해제 → fold3 trades 변화 확인
  - 또는: trend_confirm_bars=1로 완화 → 신호 민감도 증가

#### F(리서치): cmf BTC-특이성 분석 및 실전 배포 준비
- **Cycle 315 C 결론**: cmf 4h는 BTC 전용 (ETH: -4.26, SOL: -7.47)
  - Bundle OOS 5/5 PASS: 2023-2024 BTC 상승장에 특화 가능성
  - Paper sim BTC 4h 1/8 PASS: 210일 학습 기간에서 cmf 파라미터 최적화 안됨
  - 실전 배포 전 더 긴 OOS 검증 필요 (2024 이후 데이터)
- **F 작업**:
  1. 현재 2/5 PASS 확정 전략 (cmf, supertrend_multi) 실전 투입 조건 재검토
  2. 슬리피지 99% HIGH 원인 분석 (paper_sim adaptive_slippage 로직 검토)
     - cmf 4h BTC: high slippage 99.4% → 실거래 슬리피지 추정치 과도할 수 있음
  3. price_cluster 4h Bundle OOS 평가 결과 반영

### ⚠️ 주의 사항 (Cycle 316)
- **ATR_THRESHOLD**: 현재 0.95 (기본값 복원) — `atr_threshold` 파라미터는 유지, 기본값 사용
- **NR_SCAN_WINDOW**: 현재 3 (변경 금지)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 315 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}`
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
  - `relative_volume: {"rvol_buy_sell": 1.2}`
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
  - `order_flow_imbalance_v2: {"trend_span": 20}`
  - `cmf: {"buy_thresh": 0.10}`
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 315 atr_threshold 실험 후 복원):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← atr_threshold 기본값(0.95) 사용
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (변경 없음)
- **Bundle OOS 실행 시 `--csv-dir data/historical` 필수** (5-fold 4h 구조, 2023~2024 실제 BTC)
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 315)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일, --csv-dir data/historical): **0/22 PASS**
  - rank1: price_cluster (Sharpe=0.59, 3/8, PF=1.18, return=+4.50%)
  - rank2: supertrend_multi (Sharpe=0.32, 2/8, PF=1.14, return=+5.26%) ← 수익률 1위
  - narrow_range: rank9 (Sharpe=-0.42, 0/8, PF=0.99) — 기본값(0.95) 상태
  - 주 실패 원인: PF < 1.5 (1h BTC 구조적 문제)
- Paper Sim BTC 4h cmf 단독 (Cycle 315 C): **0/1 PASS**
  - cmf BTC 4h: 1/8 windows PASS, avg Sharpe=0.74 → FAIL
  - cmf ETH/SOL: 0/8 FAIL (BTC-특이성 확인)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **2/5 PASS** (Cycle 314 동일)
  - cmf: 5/5 PASS (avg=2.508, std=1.888) ← 안정적
  - supertrend_multi: 3/3 valid PASS (avg=3.674, std=1.860) ← 안정적
  - narrow_range (atr_threshold=1.05 실험 후 복원): FAIL (avg=-2.118, std=3.889)
- **실전 투입 우선순위**: supertrend_multi 4h rank1 (avg=3.674), cmf 4h rank2 (avg=2.508, BTC 전용)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)
- Paper simulation 4h 단독: `--timeframe 4h --strategies cmf` 단독 실행 (~2분)
