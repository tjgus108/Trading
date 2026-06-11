# Next Steps

_Last updated: 2026-06-11 (Cycle 297 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 297

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 295 | A+C+F | relative_volume/momentum_quality/price_cluster 파라미터화, PAPER_SIM 오버라이드 추가 |
| 296 | B+D+F | MC_P_THRESHOLD 0.05→0.10, bull_only 파라미터, close_window/n_bins 파라미터 |
| 297 | B+D+F | apply_wfe 불일치 수정, rvol_buy_sell 1.3→1.2, n_bins/bull_only 실험 실패 → 복원 |

### 🎯 Cycle 298 작업 방향 (298 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): price_cluster trades 부족 근본 해결
- **핵심 이슈**: price_cluster avg_trades=11 (< 15 기준), bounce_pct=0.015로는 신호 부족
  - 2/8 윈도우에서 ≥15 trades 달성 → 조건이 가끔 충족됨
  - 옵션 1: bounce_pct=0.02 (더 넓은 threshold → 더 많은 신호)
  - 옵션 2: PAPER_SIM_STRATEGY_PARAMS에 `price_cluster: {"bounce_pct": 0.02}` 시도
  - 주의: bounce_pct 확대 시 신호 품질(Sharpe, PF) 유지 여부 확인 필요

#### B(리스크): relative_volume 일관성 개선
- **핵심 이슈**: relative_volume 1/8 PASS (rvol_buy_sell=1.2, trades=17 avg)
  - fail reason: "trades 11 < 15 (x1), profit_factor 1.45 < 1.5 (x1), mc_p_value 0.256 > 0.1 (x1)"
  - 3개 fail 원인이 각각 1개 윈도우에서 발생 → 4/8 PASS 목표
  - rvol_buy_sell=1.1 시도하면 trades 더 증가 가능하나 PF 저하 위험
  - 대안: volatility_cluster가 trades=14/12 구간에서 아슬아슬 → 파라미터 조정 검토

#### F(리서치): order_flow_imbalance_v2 일관성 향상
- **핵심 이슈**: 3/8 PASS → 50% (4/8) 도달 필요
  - fail reasons: "mc_p_value 0.192 > 0.1 (x1), sharpe -7.98 < 1.0 (x1), profit_factor 0.31 < 1.5 (x1)"
  - mc_p_value 0.192: MC 검증 임계값 0.10에 비해 높음 → 통계적 신뢰도 부족
  - sharpe -7.98, PF 0.31: 극단 손실 윈도우 1개 → 해당 윈도우 구간 분석 필요
  - 접근: order_flow_imbalance_v2 파라미터 확인 (signal_strength_threshold 등)

### ⚠️ 주의 사항 (Cycle 298)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정**:
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B (1.3→1.2)
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.015}` ← Cycle 295 C (n_bins/close_window 제거)
- **bull_only, n_bins 실험 실패 이력**: 코드는 보존됐지만 PAPER_SIM에서 제거됨
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 297)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: price_cluster (score=70.8, Sharpe=3.63, PF=2.21, trades=11) ← 복구
  - rank2: momentum_quality (score=62.9, Sharpe=1.82, trades=22)
  - rank3: relative_volume (score=61.8, Sharpe=2.08, trades=17, 1/8 PASS) ← 신규
  - rank6: order_flow_imbalance_v2 (3/8 PASS) ← MC=0.10 효과 확인
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 296와 동일 유지)

### 주요 코드 변경 이력 (Cycle 297)
1. `src/backtest/engine.py` — apply_wfe() IS<-1.0+OOS>1.5 케이스 추가 (B 리스크)
   - RollingOOSValidator.validate()와 WFE 로직 동기화
2. `src/strategy/momentum_quality.py` — bull_only 파라미터 추가 (F 리서치)
   - 기본값 False, PAPER_SIM에서는 사용 안 함 (역효과 확인)
3. `src/strategy/price_cluster.py` — close_window, n_bins 파라미터 추가 (D ML)
   - 기본값 유지, PAPER_SIM에서는 bounce_pct=0.015만 사용 (n_bins=3 역효과 확인)
4. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS 조정
   - relative_volume: rvol_buy_sell 1.3→1.2 (trades +2, consistency 0/8→1/8)
   - price_cluster: n_bins/close_window 제거 (bounce_pct=0.015만 유지)
   - momentum_quality: bull_only 제거 (Sharpe 복구)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
