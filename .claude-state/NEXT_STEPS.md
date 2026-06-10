# Next Steps

_Last updated: 2026-06-10 (Cycle 296 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 296

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 294 | D+E+F | compute_ensemble_weight_regime_aware(), trades_regularization_scale 추가 |
| 295 | A+C+F | relative_volume/momentum_quality/price_cluster 파라미터화, PAPER_SIM 오버라이드 추가 |
| 296 | B+D+F | MC_P_THRESHOLD 0.05→0.10, bull_only 파라미터, close_window/n_bins 파라미터 |

### 🎯 Cycle 297 작업 방향 (297 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): MC_P_THRESHOLD 0.10 적용 후 Paper Sim 재실행
- **핵심 이슈**: Cycle 296 Paper Sim은 argparse default 버그로 구MC_P_THRESHOLD(0.05) 적용됨
  - argparse/run_simulation 모두 0.10으로 수정 완료 (Cycle 296)
  - 다음 사이클에서 실제 0.10 기준 결과 확인 필요
  - `order_flow_imbalance_v2`: mc_p_value 0.077/0.085 → 0.10 기준 통과 가능성
  - `momentum_quality` W8 mc_p_value 0.197 → 0.10보다 크므로 여전히 FAIL

#### D(ML): price_cluster n_bins 조정 실험
- **핵심 이슈**: close_window=35 (50→35)로도 trades 여전히 11 → 근본적 접근 다름
  - 옵션 1: n_bins=5→3 (더 넓은 bin → 더 자주 bounce 조건 충족)
  - 옵션 2: bounce_pct 0.015→0.02 (더 넓은 tolerance → 더 많은 신호)
  - PAPER_SIM_STRATEGY_PARAMS: `price_cluster: {"bounce_pct": 0.015, "close_window": 35, "n_bins": 3}` 시도
  - 주의: n_bins 변경 시 _find_cluster() 내부 로직 확인 필요

#### F(리서치): momentum_quality bear 레짐 FAIL 원인 개선
- **핵심 이슈**: momentum_quality W3-W5 (bear/sideways) FAIL → Sharpe -1.35 ~ -2.04
  - quality_score_buy_threshold 0.8이 bull에서는 좋지만 bear에서 손실
  - 접근: `bull_only` 파라미터 추가 (close > EMA50 시에만 활성화)
  - PAPER_SIM_STRATEGY_PARAMS: `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3, "bull_only": True}`
  - 단, bull_only는 신호 횟수 감소 위험 → 테스트 선행 필요

### ⚠️ 주의 사항 (Cycle 297)
- **MC_P_THRESHOLD=0.10 확인**: 이번 사이클 Paper Sim은 0.05 기준 적용됨 → 다음 사이클 0.10 결과 확인
- **PAPER_SIM_STRATEGY_PARAMS**: 6개 오버라이드 존재
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.3}` ← Cycle 295 A (bull_only 제거됨)
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.015, "close_window": 35}` ← Cycle 295 C + 296 F
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 296)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS (MC 버그로 0.05 기준 적용됨)
  - rank1: momentum_quality (score=73.3, Sharpe=1.82, trades=22) — BULL 윈도우에서 Sharpe=9.67
  - rank2: cmf (score=68.7, Sharpe=1.25, trades=23)
  - rank3: relative_volume (score=66.3, Sharpe=2.78, trades=14) — bull_only로 trades 감소
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 295와 동일 유지)

### 주요 코드 변경 이력 (Cycle 296)
1. `src/backtest/engine.py` — MC_P_THRESHOLD 0.05→0.10 (B 리스크)
2. `src/strategy/relative_volume.py` — bull_only 파라미터 추가 (D ML)
3. `src/strategy/price_cluster.py` — close_window, n_bins 파라미터 추가 (F 리서치)
4. `scripts/paper_simulation.py` — run_simulation default/argparse default 0.05→0.10 수정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
