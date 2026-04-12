# Cycle 116 Result

## [2026-04-12] WalkForward IS<=0 오분류 수정

- `src/backtest/walk_forward.py` line 186-191: IS<=0 시 ratio=0.0 고정 버그 수정
- IS<=0, OOS>0 → ratio=1.0 (non-overfit)
- IS<=0, OOS<=0 → ratio=0.0 (overfit)
- 테스트 추가: `tests/test_walk_forward.py::test_ratio_negative_is_positive_oos` PASSED

## Previous: lob_maker Strategy (FAIL)
- Return: +3.16%, Sharpe: 0.97, PF: 1.17 (need ≥1.5), MDD: 8.1%
- Deprecated: 실제 LOB 데이터 없이는 신뢰 불가

## Next Steps
1. RVOL 전략 구현: src/strategy/rvol_breakout.py
2. 조건: RVOL >= 2.0 + 가격 20일 고점 돌파 → BUY, RVOL >= 2.0 + 20일 저점 이탈 → SELL
3. 백테스트 목표: Sharpe>=1.0, MDD<=20%, PF>=1.5
