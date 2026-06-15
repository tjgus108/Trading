# Current Cycle Briefing

_Cycle 314 | 2026-06-15 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML) — vol_spike_mult 실험 (효과 없음 확인)
- `src/strategy/narrow_range.py` `vol_spike_mult` init 파라미터 추가 (클래스 상수 대신)
- `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]["vol_spike_mult"] = 0.5` 실험 후 복원
- **결론**: vol_spike_mult는 confidence 결정에만 사용 (필터 아님) → trades 증가 불가
- 실제 binding constraint는 ATR_THRESHOLD=0.95 → 다음 실험 후보

### E(실행) — live_paper_trader.py --timeframe 4h 지원 추가
- `LivePaperTrader.__init__()` 에 `timeframe` 파라미터 추가
- `fetch_latest_candles()` 2개 호출점 + `_auto_retrain()` → `timeframe=self.timeframe` 전달
- `main()` argparse에 `--timeframe` 추가
- **효과**: `python3 scripts/live_paper_trader.py --timeframe 4h` 실행 가능 (supertrend_multi 4h 투입 준비)

### F(리서치) — cmf 4h Bundle OOS PASS 확인
- Bundle OOS 5-fold (--csv-dir data/historical) 실행 결과:
  - **cmf: 5/5 PASS** (avg=2.508, PF=1.387) — relaxed WFE=0.4 기준
  - **supertrend_multi: 3/5 PASS** (avg=3.674, PF=2.475) — 지속
  - narrow_range: FAIL (avg=-1.927, vol_spike_mult 실험 효과 없음)

## 시뮬레이션 요약

| 구분 | 결과 |
|------|------|
| 테스트 | 8413 passed, 23 skipped (회귀 없음) |
| Paper Sim 1h PASS | 0/22 |
| Bundle OOS 4h PASS | 2/5 (cmf, supertrend_multi) |
| rank1 (1h) | price_cluster (Sharpe=0.59, PF=1.18, 3/8) |
| rank2 (1h) | supertrend_multi (Sharpe=0.32, PF=1.14, 2/8) |

## 다음 사이클 (315) 핵심 포인트

- **A(품질)**: narrow_range `ATR_THRESHOLD` 파라미터화 + 0.95→1.05 실험
- **C(데이터)**: cmf WFE 완화(0.4) 기준 재검토 — 표준(0.5) 강화 시 PASS/FAIL 재확인
- **F(리서치)**: paper_simulation.py --timeframe 4h로 cmf/supertrend_multi 4h 결과 확인
