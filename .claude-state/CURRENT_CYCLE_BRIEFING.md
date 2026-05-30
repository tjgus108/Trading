======================================================================
🔄 CYCLE 247 — 2026-05-30
======================================================================

## 이번 사이클 배정 카테고리

247 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)

## 핵심 작업 완료

### [B] kelly_fraction_multiplier → manager.py 연결
- 갭: Cycle 246에서 `get_kelly_fraction_multiplier()` 추가했으나 `evaluate()`에서 미호출
- 수정: kelly_sizer + drawdown_monitor 모두 있을 때 MDD > 8% → position_size × 0.5 추가 적용
- 효과: MDD 8~10% 구간 → 총 0.25x 복합 축소 (mdd_warn 0.5x × kelly_frac 0.5x)
- 신규 테스트 2개: 통합 검증

### [D] paper_simulation.py MC CLI 인수 추가
- --mc-min-trades N: BacktestEngine.mc_min_trades 제어
- --mc-block-size N: BacktestEngine.mc_block_size 제어
- 모듈 상수 MC_MIN_TRADES=0, MC_BLOCK_SIZE=1 추가

### [F] value_area min_oos_trades 분석
- --min-trades CLI 이미 존재 → --min-trades 5로 즉시 완화 가능
- 합성 데이터 IS Sharpe 음수 → 실거래소 데이터 필요

## 시뮬레이션 결과

### Paper SIM BTC 1h (합성)
- 0/22 PASS
- Composite #1: value_area (Score 73.9, AvgSharpe 4.39, AvgTrades 27, AvgMDD 3.1%)

### Bundle OOS BTC 4h (합성)
- 0/5 PASS (IS Sharpe 100% 음수: elder_impulse/wick_reversal/narrow_range)
- value_area fold 6 PASS (OOS Sharpe=1.775), 전 fold trades<10

## 테스트
8339 passed, 23 skipped (신규 2개 포함)

## 다음 사이클: 248 (C+B+F)
- C: 합성 데이터 IS Sharpe 음수 해결 (bull regime 지속 기간 증가)
- B: kelly_fraction_multiplier 복합 효과 백테스트 정량화
- F: --min-trades 5 value_area 완화 검증
