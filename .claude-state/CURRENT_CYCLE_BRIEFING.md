======================================================================
🔄 CYCLE 194 — 2026-05-21T20:30:00Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)
- D(ML): 온체인 피처 통합 + OOS std 필터 개선
- E(실행): PaperTrader KellySizer 통합
- F(리서치): ML 프로덕션 배포 아키텍처

## 완료된 작업

### D(ML): 온체인 피처 통합
- `src/ml/features.py`: exchange_netflow→netflow_zscore, sopr→sopr_delta 추가
- `REGIME_OPTIONAL_FEATURES`: bull→sopr_delta, bear/crisis→netflow_zscore
- 선택적: df에 컬럼 없으면 자동 생략

### D(ML): OOS Sharpe std 필터 개선
- `src/backtest/walk_forward.py` RollingOOSValidator:
  - 거래 0건 폴드를 OOS std 계산에서 제외 → false-fail 감소
  - traded_sharpes = [f.oos_sharpe for f in folds if f.oos_trades >= 1]

### E(실행): PaperTrader + KellySizer 통합
- `src/exchange/paper_trader.py`:
  - kelly_sizer 파라미터 추가
  - BUY: compute_dynamic(capital, price) → quantity 결정
  - SELL: record_trade(pnl_pct) → rolling 기록
  - get_summary(): kelly_sizer_active/adjustments 추가

### 테스트: 7710 PASS (9개 신규 추가)

## SIM 결과
- Paper SIM: 0/22 PASS — value_area +0.36% 최선
- Bundle OOS: 0/5 PASS — std 3.2~6.2 (개선 후 다음 사이클 재검증)

## 다음: Cycle 195 A(품질) + C(데이터) + F(리서치)
