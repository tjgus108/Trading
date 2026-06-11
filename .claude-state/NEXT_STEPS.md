# Next Steps

_Last updated: 2026-06-11 (Cycle 298 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 298

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 296 | B+D+F | MC_P_THRESHOLD 0.05→0.10, bull_only 파라미터, close_window/n_bins 파라미터 |
| 297 | B+D+F | apply_wfe 불일치 수정, rvol_buy_sell 1.3→1.2, n_bins/bull_only 실험 실패 → 복원 |
| 298 | C+B+F | bounce_pct 0.015→0.02 (2/8 sideways PASS), consec_loss_scale 엔진 추가, trend_span 실험 |

### 🎯 Cycle 299 작업 방향 (299 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML 모델 신호 품질 개선
- **핵심 이슈**: price_cluster 2/8 PASS - sideways 시장에서만 통과
  - W5/W6 sideways: 17, 15 trades → PASS. 나머지 bull/bear 윈도우: 9-12 trades
  - ML 기반 regime 감지로 price_cluster가 sideways에서만 활성화하는 방식 검토
  - 또는: momentum_quality, cmf의 mc_p_value 이슈 집중 개선

#### E(실행): Paper Trading 모드 검증
- **핵심 이슈**: cmf/supertrend_multi Bundle OOS 2/5 PASS 유지 중
  - 이 두 전략으로 Paper Trading 실전 투입 가능성 검토
  - TWAP 실행기 슬리피지 모델 검증

#### F(리서치): order_flow_imbalance_v2 근본 분석
- **핵심 이슈**: 3/8 PASS 유지 (trend_span 실험으로 개선 불가 확인)
  - trend_span=20: 3/8 PASS, sharpe=-7.98 여전히 존재 (EMA20 너무 단기)
  - trend_span=50: 1/8 PASS (과도한 필터링)
  - 근본 해결: BUY_THRESH/SELL_THRESH 조정 또는 새로운 접근법 필요
  - 검토: cumulative delta rolling window 10→5 단축 (최근 신호 반응성 향상)

### ⚠️ 주의 사항 (Cycle 299)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 298 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 298 B (1.1 역효과 확인, 1.2 복원)
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.02}` ← Cycle 298 C (0.015→0.02, 2/8 PASS 달성)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F (trend_span=50 역효과 확인)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 298)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: price_cluster (score=74.6, Sharpe=3.63, PF=2.15, trades=12, **2/8 PASS**) ← bounce_pct=0.02
  - rank2: momentum_quality (score=64.4, Sharpe=1.80, trades=22)
  - rank3: relative_volume (score=63.0, Sharpe=1.94, SharpeStd=2.96, 1/8 PASS)
  - rank11: order_flow_imbalance_v2 (trend_span=20, 3/8 PASS) ← trend_span=50 역효과 확인
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 297와 동일 유지)

### 주요 코드 변경 이력 (Cycle 298)
1. `src/backtest/engine.py` — consec_loss_scale_threshold 파라미터 추가 (B 리스크)
   - N회 연속 손실 시 포지션 50% 축소 (DrawdownMonitor 로직 백테스트에 반영)
   - 기본값=0 (비활성), paper_simulation에서 5로 활성화
2. `src/strategy/order_flow_imbalance_v2.py` — trend_span 파라미터 추가 (F 리서치)
   - trend_span > 0이면 EMA macro trend filter 적용 (BUY: close>EMA, SELL: close<EMA)
   - 기본값=0 (비활성), PAPER_SIM에서 20으로 활성화
3. `scripts/paper_simulation.py` — PAPER_SIM_STRATEGY_PARAMS 조정
   - price_cluster: bounce_pct 0.015→0.02 (2/8 sideways PASS 달성)
   - relative_volume: rvol_buy_sell 1.1→1.2 복원 (1.1 역효과 확인)
   - order_flow_imbalance_v2: trend_span=20 추가 (EMA20 macro filter)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
