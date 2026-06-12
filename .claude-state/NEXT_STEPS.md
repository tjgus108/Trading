# Next Steps

_Last updated: 2026-06-12 (Cycle 304 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 304

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 302 | B+D+F | n_bins=7+atr_bounce_factor=1.5 역효과 복원, DrawdownMonitor tiered halt 개선, price_cluster 그리드 추가 |
| 303 | C+B+F | close_window=40 역효과(Sharpe -61%) 확인→50 복원, tiered halt 회복 테스트 2개 추가 |
| 304 | D+E+F | bounce_pct=0.030 역효과(Sharpe 0.53) 확인→0.025 복원, WF 그리드 [50,60] 업데이트, narrow_range ATR 필터 추가 |

### 🎯 Cycle 305 작업 방향 (305 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 품질 재검증
- **narrow_range trend_regime_filter 파라미터 OOS 효과 측정**:
  - Cycle304 F에서 TREND_REGIME_MAX=1.4 추가. OOS에서 fold1/4 FAIL 저감 여부 확인
  - paper_simulation.py PAPER_SIM_STRATEGY_PARAMS에 `"narrow_range": {"trend_regime_max": 1.4}` 추가 실험
  - 주의: 기본값은 0.0(비활성). 활성화 시 신호 감소 가능성 있음
- **Bundle OOS narrow_range 재실행**: trend_regime_max=1.4 적용 시 fold1/4 개선 여부

#### C(데이터): 데이터/인프라 개선
- **close_window=60 탐색**:
  - walk_forward 그리드 [50,60]으로 업데이트됨 (Cycle304 D)
  - paper_simulation.py에서 close_window=60 단독 실험 (close_window=50 기준선 대비)
  - 기대: 더 긴 price memory → support/resistance 안정성 향상
  - 위험: 신호 지연 가능성 (60봉 = 2.5일 4h봉)
- **vol_atr_trend_min 재실험**:
  - walk_forward 그리드에 [1.5, 2.0] 있음. 2.0 탐색 여부 결정

#### F(리서치): 최신 연구 기반 개선
- **bounce_pct 탐색 완료 분석**:
  - 0.020: 기준 (Cycle298)
  - 0.025: 최적 (Cycle301, Sharpe +10%, PF +11%)
  - 0.030: 역효과 (Cycle304, Sharpe 3.76→0.53, trades 12→50)
  - 결론: 0.025가 BTC 4h price cluster의 sweet spot. 추가 탐색 불필요
- **narrow_range 고변동성 분석 심화**:
  - fold1(2023-08-29~10-27) BTC 급등 구간에서 NR false breakout
  - TREND_REGIME_MAX=1.4 효과 → 다음 시뮬에서 검증

### ⚠️ 주의 사항 (Cycle 305)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 304 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← bounce_pct 0.025 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 304)
- 테스트: **8394 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - bounce_pct=0.030 역효과: price_cluster Sharpe 3.76→0.53, trades 12→50
  - 복원 후: bounce_pct=0.025 최적 확정
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)

### 주요 코드 변경 이력 (Cycle 304)
1. `src/backtest/walk_forward.py` — price_cluster close_window 그리드 [40,50]→[50,60] (D(ML))
   - close_window=40 역효과 확인(Cycle303) → 40 제거, 60 추가
2. `src/strategy/narrow_range.py` — trend_regime_max 고변동성 억제 필터 추가 (F(리서치))
   - ATR/ATR_MA(20) > TREND_REGIME_MAX(1.4) 시 NR 신호 억제
   - 기본값: trend_regime_max=0.0 (비활성), 파라미터로 활성화 가능
3. `scripts/paper_simulation.py` — bounce_pct=0.030 실험 후 역효과 확인 → 0.025 복원 (D(ML))

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 3-4분 소요 (BTC 단일)

### bounce_pct 탐색 완료 역사 (price_cluster)
| 실험 | bounce_pct | Sharpe | PF | Trades | 결론 |
|------|-----------|--------|-----|--------|------|
| 기본 | 0.015 | ~2.x | ~1.7 | ~10 | 초기 기준선 |
| Cycle298 C | 0.020 | - | - | - | 기준선 업데이트 |
| Cycle301 B | 0.025 | 3.76 | 2.28 | 12 | 최적 (+10%/+11%) |
| Cycle304 D | 0.030 | 0.53 | - | 50 | 역효과 (false signal 급증) |
| 결론 | **0.025** | - | - | - | **탐색 완료, 고정** |
