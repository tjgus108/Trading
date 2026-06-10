# Next Steps

_Last updated: 2026-06-10 (Cycle 295 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 295

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 293 | C+B+F | --verbose-windows 옵션, VolTargeting.for_timeframe(), Paper Sim FAIL 원인 분석 완료 |
| 294 | D+E+F | compute_ensemble_weight_regime_aware(), trades_regularization_scale 추가 |
| 295 | A+C+F | momentum_quality rank1 점프, relative_volume PF+trades 기준 달성, pf_regularization_scale 추가 |

### 🎯 Cycle 296 작업 방향 (296 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): Consistency 1/8 → 4/8 달성 핵심 장벽 분석
- **핵심 이슈**: Paper Sim 모든 전략 consistency 0~1/8 — 윈도우간 심한 불일치
  - momentum_quality: Sharpe=2.12 평균이지만 SharpeStd=3.31 — 1개 윈도우만 통과
  - relative_volume: PF=1.53 달성, trades=15 달성, 그러나 Sharpe 윈도우간 불일치 → 0/8
  - 근본 원인: 레짐 변화 (Bull W1-W4 vs Sideways W5-W7 vs 회복 W8)
  - **해결 방향**: 포지션 사이징 개선 — DrawdownMonitor로 sidebar 레짐에서 포지션 자동 축소
  - `src/risk/drawdown_monitor.py` 확인 후 연속 FAIL 윈도우 시 사이즈 축소 로직 추가
  - Kelly Sizer에 레짐별 multiplier 적용 (SIDEWAYS: 0.5배, BULL: 1.0배)

#### D(ML): momentum_quality PF 1.41 → 1.5 달성
- **핵심 이슈**: momentum_quality PF=1.41 (gap=0.09) — 가장 유망한 전략
  - `optimize_momentum_quality()` 실행: DEFAULT_GRIDS로 IS PF 최적화
  - `pf_regularization_scale=0.1` 효과 검증: Bundle OOS에서 PF 개선 여부 확인
  - 실행 명령: `python3 -c "from src.backtest.walk_forward import optimize_momentum_quality; ..."`
  - 최적 buy_threshold (0.8/0.9/1.0) vs OOS PF 관계 분석
  - `scripts/run_bundle_oos.py`에 momentum_quality 추가 (5-strategy → 6-strategy)

#### F(리서치): Window consistency 개선 전략 조사
- Cycle 295 분석 결론:
  - trades 병목 해소 진행 중 (relative_volume=15, wick_reversal=16, htf_ema=14)
  - **신규 핵심 병목: PF 일관성** — 1~2개 윈도우에서만 PF ≥ 1.5 달성
  - momentum_quality: buy_threshold=0.8이 최선. PF는 IS 단계 최적화로 개선 가능성
  - relative_volume: 이미 PF+trades 달성. Sharpe consistency가 유일한 장벽
  - 제안: Sharpe consistency 개선을 위한 TP/SL 파라미터 튜닝 조사
    - ATR multiplier for TP: 현재 값 확인 후 상향 시 PF 개선 여부 분석
    - Walk-forward train 기간 조정: 현재 7개월 → 5개월으로 단축 시 최근성 증가

### ⚠️ 주의 사항 (Cycle 296)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **PAPER_SIM_STRATEGY_PARAMS 현재값 유지** (Cycle 295 오버라이드 활성 중)
  - momentum_quality: {buy_threshold: 0.8, sell_threshold: -0.4}
  - relative_volume: {rvol_threshold: 1.4}
  - wick_reversal: {min_wick_ratio: 0.45}
  - htf_ema: {cross_pct: 0.25}
  - value_area: {min_breach: 1.0}
  - price_cluster: {n_bins: 8, bounce_pct: 0.015}
- **신규 전략 파일 생성 금지** — 기존 파라미터 오버라이드로만 접근
- **pf_regularization_scale=0.1** optimize_momentum_quality에만 적용, 다른 전략 기본값 0.0 유지

### 핵심 메트릭 (Cycle 295)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: momentum_quality (score=78.7, Sharpe=2.12, PF=1.41, trades=22) ← 신규 1위
  - rank2: cmf (score=71.3, Sharpe=1.25, PF=1.24, trades=23)
  - rank4: relative_volume (score=61.8, Sharpe=1.94, PF=1.53, trades=15) ← PF+trades 기준 달성!
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024): **2/5 PASS**
  - cmf: PASS avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: PASS avg=3.674, std=1.860, WFE=2.116

### 주요 코드 변경 이력 (Cycle 295)
1. `src/strategy/htf_ema.py` — `__init__(cross_pct=0.5)` 추가 (A 품질)
2. `src/strategy/relative_volume.py` — `__init__(rvol_threshold=1.6)` 추가 (A 품질)
3. `src/strategy/momentum_quality.py` — `__init__(buy_threshold, sell_threshold, ...)` 추가 (C 데이터)
4. `src/strategy/price_cluster.py` — `__init__(n_bins, bounce_pct)` 추가 (C 데이터)
5. `scripts/paper_simulation.py` — `PAPER_SIM_STRATEGY_PARAMS` 6개 전략 오버라이드 추가
6. `src/backtest/walk_forward.py` — `pf_regularization_scale` 파라미터 + `optimize_momentum_quality()` 추가 (C+F)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 8-10분 소요
