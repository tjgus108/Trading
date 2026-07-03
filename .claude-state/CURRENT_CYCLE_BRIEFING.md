# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 388 완료)_

## 현재 상태

- **완료된 사이클**: 388
- **다음 사이클**: 389 (389 mod 5 = 4 → D+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8491개 (+9 from Cycle388)

## Cycle 388 주요 결과

### A(품질): consec_loss_scale_threshold 테스트 추가
- BacktestEngine 2단계 연속손실 스케일링 (Cycle338 B 기능) 완전 커버리지
  - loss_scale_half_count (0.75x): threshold//2 이상 연속 손실 시 트리거
  - loss_scale_full_count (0.50x): threshold 이상 연속 손실 시 트리거
- 5개 테스트 추가 (test_backtest_engine.py)

### B(리스크): KellySizer Bayesian shrinkage 경계값 테스트
- MIN_TRADES_FOR_KELLY=15 경계 검증:
  - n=14 < 15: shrink_factor = 14/(14+15) = 0.483 → size 축소 확인
  - n≥15: raw win_rate 직접 사용
- 4개 테스트 추가 (test_kelly_sizer_regime_edge_cases.py)

### F(리서치): price_cluster vol_regime_filter=True 실험 (핵심 발견)
- 최근 2400봉(~100일) BTC 1h 데이터 실험:
  - **filter=T, bp=0.006, min=1.2: Sh=2.10, PF=1.52, Tr=51 [PASS!]**
  - filter=F, bp=0.010 (baseline): Sh=1.70, PF=1.37 [FAIL]
  - filter=T, bp=0.010: PF=1.48 (거의 PASS), filter=T, bp=0.008: PF=1.47
- **이전 미시험 조합**: bounce_pct=0.006 + vol_regime_filter=True 조합이 유망
- 전체 WFO 검증 필요 (paper_simulation.py 8개 윈도우)

## 다음 사이클 (389) 핵심 과제

1. **D(ML)**: `paper_simulation.py`에서 price_cluster params를 `vol_regime_filter=True, bounce_pct=0.006`으로 변경 후 실행
   - PASS 확인 시: 확정. FAIL 시: params 복원
2. **E(실행)**: paper_trader 추가 테스트
3. **F(리서치)**: WFO 결과 분석 및 다음 방향 결정
