# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 389 완료)_

## 현재 상태

- **완료된 사이클**: 389
- **다음 사이클**: 390 (390 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8496개 (+5 from Cycle389)

## Cycle 389 주요 결과

### D(ML): price_cluster vol_regime_filter=True + bounce_pct=0.006 WFO 전체 검증

- `paper_simulation.py` price_cluster 파라미터: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}`
- **WFO 전체(8 윈도우) 결과**:
  - Sh=0.95(+0.08), PF=1.33(+0.13), Tr=34, Consistency=2/8 → FAIL
  - baseline(filter=False, bp=0.010): Sh=0.87, PF=1.20 대비 개선
- **결론**: 방향은 맞지만 PF binding (1.33 < 1.5). 다음: bounce_pct=0.004 탐색
- **최근 100일(Cycle388 F)**: Sh=2.10, PF=1.52 — favorable period 효과 확인

### E(실행): PaperTrader load_state 스키마 검증 테스트 추가

- `tests/test_paper_trader.py` 5개 테스트 추가:
  - invalid initial_balance/balance 타입 → ValueError
  - positions/avg_entry 심볼 불일치 → 합집합 복구
  - kelly/vol_targeting 카운터 복원 검증
  - schema_version > 1 → 경고만, raise 없음

### F(리서치): WFO 분석 결론

- price_cluster filter=True+bp=0.006: 방향 유효, 아직 PASS 미달
  - FAIL 원인: PF<1.5 (binding), Sh<1.0 (일부 윈도우), Consistency 2/8
  - OOS SharpeStd=2.20 (허용 범위)
- 다음 실험: bounce_pct=0.004 (신호 빈도↑ → PF 개선 기대)

## 다음 사이클 (390) 핵심 과제

1. **A(품질)**: 테스트 커버리지 추가 (BacktestEngine 또는 WalkForwardOptimizer)
2. **C(데이터)**: paper_simulation.py price_cluster → `{"vol_regime_filter": True, "bounce_pct": 0.004, "vol_atr_trend_min": 1.2}` 실험
3. **F(리서치)**: PF 개선 경로 분석, 각 윈도우 FAIL 원인 패턴 파악
