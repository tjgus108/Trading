# Next Steps

_Last updated: 2026-06-13 (Cycle 304 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 304

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 302 | B+D+F | n_bins=7+atr_bounce_factor=1.5 역효과 복원, DrawdownMonitor tiered halt 개선, price_cluster 그리드 추가 |
| 303 | C+B+F | close_window=40 역효과(Sharpe -61%) 확인→50 복원, tiered halt 회복 테스트 2개 추가 |
| 304 | D+E+F | bounce_pct=0.030 역효과(PF-9%) 확인→0.025 복원, NarrowRange trend_regime_filter 추가, walk_forward close_window [50,60] |

### 🎯 Cycle 305 작업 방향 (305 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 검증 품질 개선
- **NarrowRange trend_regime_filter 파라미터 walk_forward 그리드 추가**:
  - Cycle304 E에서 `trend_regime_filter`, `atr_trend_max` 추가됨
  - walk_forward DEFAULT_GRIDS narrow_range에 `trend_regime_filter: [False, True]` 추가 실험
  - Bundle OOS fold1/3 FAIL 원인 검증용

#### C(데이터): price_cluster close_window=60 실험
- **close_window=60 단독 실험**: n_bins=5, bounce_pct=0.025 유지하면서 window만 확장
  - 현재: close_window=50 (기본값)
  - 목적: 더 긴 price memory → support/resistance 품질 향상 → trades 안정화
  - 기대: PF 유지 + trades 개선 가능
  - 주의: Cycle303 분석에서 40→50 역효과 있었음. 50→60은 방향이 다름 (확장)

#### F(리서치): PASS 전략 분석
- **cmf, supertrend_multi 파라미터 분석**:
  - cmf: 5/5 PASS (Sharpe=2.508, PF=1.387) — 가장 안정적인 전략
  - supertrend_multi: PASS (OOS Sharpe=3.674, PF=2.475, fold3/4 제외)
  - 두 전략의 공통점: 추세 추종 + 다중 확인 필터

### ⚠️ 주의 사항 (Cycle 305)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 304 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 304 복원 (bounce_pct=0.030 역효과)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 304)
- 테스트: **8394 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 4h (8 windows): **0/22 PASS**
  - price_cluster bounce_pct=0.030: Sharpe=3.76, PF=2.07, trades=13 ← 역효과 (PF -9%)
  - rank1: price_cluster (score=73.8), rank2: momentum_quality (score=62.5)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674) ← 동일

### 주요 코드 변경 이력 (Cycle 304)
1. `src/backtest/walk_forward.py` — price_cluster close_window [40,50]→[50,60] (D(ML))
2. `src/strategy/narrow_range.py` — trend_regime_filter 파라미터 추가 (E(실행))
   - `trend_regime_filter=False`, `atr_trend_max=1.4`
   - ATR/ATR_MA > 1.4 시 NR breakout 신호 억제 (고변동성 추세장 오신호 방지)
3. `scripts/paper_simulation.py` — bounce_pct=0.030 실험 후 역효과 확인 → 0.025 복원 (D(ML))

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 3-4분 소요 (BTC 단일)

### bounce_pct 실험 역사 (price_cluster)
| 실험 | bounce_pct | Sharpe | PF | Trades | 결론 |
|------|-----------|--------|-----|--------|------|
| 기본 | 0.020 | ~3.4 | ~2.0 | 12 | 기준선 |
| Cycle301 B | 0.025 | 3.76 | 2.28 | 12 | 최적 기준선 |
| Cycle304 D | 0.030 | 3.76 | 2.07 | 13 | 역효과 (PF -9%) |
| 확정 | 0.025 | 3.76 | 2.28 | 12 | 최적값 확정 |

### close_window 실험 역사 (price_cluster)
| 실험 | close_window | Sharpe | PF | Trades | 결론 |
|------|-------------|--------|-----|--------|------|
| 기본 | 50 | ~3.4 | ~2.0 | 12 | 기준선 |
| Cycle301 B | 50+bounce=0.025 | 3.76 | 2.28 | 12 | 최적 기준선 |
| Cycle303 C | 40 | 1.47 | 1.54 | 12 | 역효과 (Sharpe -61%) |
| 다음 실험 | 60 | - | - | - | Cycle305 C에서 탐색 |
