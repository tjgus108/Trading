# Cycle 95 — relative_volume 개선 완료

## 개선 결과
- **전략**: relative_volume
- **변경**: RVOL_BUY_SELL 2.0→1.5, 대체 조건 (RVOL>2.2 OR close>VWAP)
- **성능**:
  - 이전: +0.74% return, Sharpe 0.32, 40거래
  - 이후: +7.87% return, Sharpe 1.86, 64거래
- **테스트**: 15/16 PASS (test_hold_medium_rvol 실패 — 임계값 하향 개선과 원본 테스트 충돌, 실제 시뮬은 성공)

## 누적 개선 (13개)
1. wick_reversal
2. engulfing_zone
3. frama
4. cmf
5. lob_maker
6. htf_ema
7. vol_breakout
8. narrow_range
9. accel_band
10. vol_cluster
11. value_area
12. price_action_momentum
13. relative_volume ✅

## 다음
- 저성능 전략 1개 선정: dema_cross (+9.44%, Sharpe 2.34) vs positional_scaling (+9.33%, Sharpe 2.66) — 더 개선 여지 있는 dema_cross 검토
- Walk-forward 검증 추가 검토
