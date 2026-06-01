# Current Cycle Briefing

_Cycle 255 — 2026-06-01_
_카테고리: A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): compute_rank_scores 0-trade 버그 수정
- `src/backtest/report.py`: silence_mask로 0-trade 전략의 인위적 고점수 방지
  - n_sharpe_adj=0.0 (trades=0이면 neutral sharpe 혜택 차단)
  - trade_gate=trades/max: MDD/stability 컴포넌트를 거래 활동으로 가중
- `tests/test_paper_simulation.py`: `test_silent_strategy_scores_below_active_strategy` 추가
- MC 테스트 25/25 통과, 전체 테스트 8367 passed

### C(데이터): 히스토리컬 CSV 파이프라인 구축
- `data/historical/binance/BTCUSDT/1h.csv` 생성 (12,000행, GARCH+regime)
  - GARCH(1,1) + regime-switching (bull 75%, bear 9%, sideways 16%)
  - validate_ohlcv: is_valid=True (violations=0, gaps=0)
- load_ohlcv_from_csv_dir() + paper_simulation --csv-dir 통합 확인
- resample_ohlcv 1h→4h 체인 검증 (3000행, valid)

### F(리서치): 시뮬레이션 결과 분석
- Paper Sim 결과:
  - BTC (GARCH CSV, 8 windows): 0/22 PASS
  - ETH (합성, 4 windows): 1/22 PASS (linear_channel_rev sharpe=2.37)
  - SOL (합성, 4 windows): **6/22 PASS** (price_action_momentum, momentum_quality, roc_ma_cross, cmf, supertrend_multi, acceleration_band)
- Bundle OOS: 0/5 PASS (narrow_range Score 85.2)
- 핵심 발견: **profit_factor < 1.5가 binding constraint** (방향은 맞는데 PF 부족)

## 다음 Cycle 256 (256 mod 5 = 1 → B+D+F)
- B: atr_multiplier_tp 확대로 PF 개선 실험
- D: SOL PASS 전략 신호 조건 ML 피처화
- F: BTC GARCH CSV로 paper_simulation 재실행
