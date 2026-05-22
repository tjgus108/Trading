# Current Cycle Briefing

_Cycle 196 — B(리스크) + D(ML) + F(리서치)_
_Date: 2026-05-22_

## 완료된 작업

### B(리스크)
1. **DrawdownMonitor rolling MDD**: `_equity_history` deque + `rolling_mdd()` 메서드 추가. `DrawdownStatus.rolling_mdd_pct` 필드로 노출.
2. **CircuitBreaker 버그 수정**: 쿨다운 중 `record_trade_result(False)` 호출 시 `_consecutive_losses=0` 즉시 적용 (기존: 무시됨).
3. **KellySizer rolling_window 테스트 5개**: small/large window, 포지션 차이, min_trades fallback, NaN 무시.

### D(ML)
1. **DualGateADWINMonitor E2E 테스트 3개**:
   - 피처 drift → retrain_count>0
   - reset() 후 should_retrain=False, count 누적 유지
   - PSI drift → AccuracyDriftMonitor retrain trigger

### F(리서치) — SIM 분석
- Bundle OOS (4h, GBM): 5/5 FAIL
  - wick_reversal fold 1 PASS (OOS 4.832) → 나머지 불안정 (-8 이하)
  - narrow_range: 전 fold 0거래 → 4h 파라미터 완화 필요
  - OOS Sharpe std 3~7 → 합성 GBM 한계

## 다음 사이클 (197)
- DrawdownMonitor rolling_window 생성자 파라미터화
- narrow_range 4h 신호 조건 분석
- RiskManager 통합 시나리오 테스트
