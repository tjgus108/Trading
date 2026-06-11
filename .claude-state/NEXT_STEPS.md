# Next Steps

_Last updated: 2026-06-11 (Cycle 298 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 298

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 296 | B+D+F | MC_P_THRESHOLD 0.05→0.10, bull_only 파라미터, close_window/n_bins 파라미터 |
| 297 | B+D+F | apply_wfe 불일치 수정, rvol_buy_sell 1.3→1.2, n_bins/bull_only 실험 실패 → 복원 |
| 298 | C+B+F | bounce_pct 0.015→0.02, rvol_buy_sell 1.2→1.1(trades↑), ofi_v2 thresh 파라미터화 |

### 🎯 Cycle 299 작업 방향 (299 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): price_cluster trades=12 돌파 — 새 피처 접근
- **핵심 이슈**: bounce_pct=0.02까지 확대해도 avg_trades=12 (< 15 기준)
  - 클러스터 발견 윈도우(close_window=50봉) 자체의 문제일 가능성
  - 옵션: 신호 발생 조건 완화 — prev_close와 cluster 경계 사이 간격을 더 넓게 허용
  - 예) prev_close >= cluster_low - threshold*2 (threshold 2배 허용)
  - 주의: 너무 완화하면 Sharpe/PF 저하 위험 → 단계적 테스트 필요

#### E(실행): relative_volume 일관성 4/8 PASS 목표
- **핵심 이슈**: rvol_buy_sell=1.1로 trades=19(avg)지만 일부 윈도우 여전히 FAIL
  - Cycle 298 1/8 PASS (win=0): consistency=1/8
  - 다음 접근: EMA 필터 강화 (현재 없음) or ATR 기반 동적 rvol threshold
  - 대안: price_action_momentum과 결합 앙상블 검토 (trades↑ 효과)

#### F(리서치): order_flow_imbalance_v2 전략 근본 분석
- **핵심 이슈**: buy_thresh 0.22 시도 → consistency 3/8→2/8 퇴보 (2024-Q1 레짐 불안정)
  - 문제 윈도우 분석: sharpe=-7.98 극단 손실 구간 어디?
  - 접근: 거래량 필터 강화 (vol_sma20 → vol_sma10, 더 빠른 반응) or 손절 조건 추가
  - 주의: order_flow_imbalance_v2 코드 자체는 파라미터화 완료 (buy_thresh 변수 사용)

### ⚠️ 주의 사항 (Cycle 299)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정**:
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.1}` ← Cycle 298 B (1.2→1.1 개선)
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.02}` ← Cycle 298 C (0.015→0.02)
- **실패 이력**: buy_thresh=0.22, bull_only, n_bins=3 — PAPER_SIM에서 제거됨 (코드는 보존)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 298)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: price_cluster (score=74.9, Sharpe=3.72, PF=2.17, trades=12, consistency=2/8)
  - rank2: momentum_quality (score=64.5, Sharpe=1.82, trades=22, consistency=1/8)
  - rank3: relative_volume (score=62.6, Sharpe=1.84, trades=19, consistency=1/8) ← rvol=1.1 유지
  - rank6: order_flow_imbalance_v2 (score=52.6, consistency=2/8) ← buy_thresh=0.22 역효과 복원
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 297과 동일 유지)

### 주요 코드 변경 이력 (Cycle 298)
1. `src/strategy/order_flow_imbalance_v2.py` — buy_thresh, sell_thresh 생성자 파라미터 추가 (F 리서치)
   - 기본값 각각 0.25/-0.25 유지, PAPER_SIM 오버라이드는 역효과로 제거
2. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS 조정
   - price_cluster: bounce_pct 0.015→0.02 (trades 11→12)
   - relative_volume: rvol_buy_sell 1.2→1.1 (trades 17→19 개선)
   - order_flow_imbalance_v2: buy_thresh=0.22 시도 → 역효과 → 제거

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
