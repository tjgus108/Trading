# Current Cycle Briefing

_Last updated: 2026-07-05 (Cycle 398 완료)_

## 현재 상태

- **완료된 사이클**: 398
- **다음 사이클**: 399 (399 mod 5 = 4 → D+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.24, PF=1.12, Trades=40 → weak_rsi_buy_max=50 실험 중 (다음 sim에서 확인)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (최신)
- **전체 테스트 수**: 8544개 (+12)

## Cycle 398 주요 결과

### C(데이터): feed.py _add_indicators() 단행 DF 경계 케이스 5개 추가

- `tests/test_feed_boundary.py`: `TestAddIndicatorsShortDf` 클래스 신규 (5 tests)
  - 1-row / 3-row df → crash 없이 컬럼 생성 확인
  - 5-row df → donchian(rolling(20)) all NaN, EWM ATR은 값 존재
  - volume_quote + volume_quote_sma20 자동 생성 확인
  - 사전 미발견: `_add_indicators()` 1행 입력 시 crash 여부 미검증

### B(리스크): kelly_sizer compute_from_trades() 엣지케이스 7개 추가

- `tests/test_kelly_sizer_regime_edge_cases.py`: `TestKellyComputeFromTrades` 클래스 신규 (7 tests)
  - 전패 입력(avg_win=0) → size=0
  - 전승 입력(avg_loss=0) → crash 없음, size>=0
  - NaN/inf 포함 입력 → 필터링 후 유한 결과
  - 빈 리스트([]) → 0.0
  - 전체 NaN → 0.0
  - 소표본(n=10) → Bayesian shrinkage 적용
  - 손익분기 트레이드([0.0×4]) → 0.0

### F(리서치): frama weak_rsi_buy_max 파라미터화

- `src/strategy/frama.py`: `weak_rsi_buy_max=40`, `weak_rsi_sell_min=60` 파라미터 추가
  - 기존: gap<1% 약한신호 → RSI<40(BUY) / RSI>60(SELL) 하드코딩
  - 변경: 파라미터화 → WFO 그리드 탐색 가능
  - 동기: BTC 1h RANGING(47.3%)에서 RSI 40-60 구간 신호 차단 → Trades 증가 가능성
- `src/backtest/walk_forward.py`: `weak_rsi_buy_max=[40, 50, 60]` 그리드 추가 (9→27 combos)
- `scripts/paper_simulation.py`: `weak_rsi_buy_max=50` 실험 파라미터 추가

## 시뮬레이션 현황 (Cycle 398 생성, baseline — 코드 변경 전 실행)

| 전략 | Sharpe | PF | Trades | Consist | Pass |
|------|--------|-----|--------|---------|------|
| roc_ma_cross | 1.81 | 2.02 | 14 | 4/8 | **PASS** |
| price_cluster | 1.06 | 1.32 | 35 | 2/8 | FAIL |
| dema_cross | 0.85 | 1.38 | 26 | 2/8 | FAIL |
| frama | 0.24 | 1.12 | 40 | 1/8 | FAIL (weak_rsi_buy_max=50 실험 → 다음 sim에서 확인) |
