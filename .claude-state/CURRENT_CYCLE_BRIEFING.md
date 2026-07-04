# Current Cycle Briefing

_Last updated: 2026-07-04 (Cycle 391 완료)_

## 현재 상태

- **완료된 사이클**: 391
- **다음 사이클**: 392 (392 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8502개 (+5)

## Cycle 391 주요 결과

### B(리스크): CircuitBreaker max_daily_trades + DrawdownMonitor set_ranging_macro_neutral 테스트 5개

- `tests/test_circuit_breaker.py`: max_daily_trades 3개 추가
  - limit 도달 시 triggered=True, 0=무제한, reset_daily() 후 초기화
- `tests/test_drawdown_monitor.py`: set_ranging_macro_neutral 2개 추가
  - |slope|<=threshold → True (cooldown 0.9x), |slope|>threshold → False (cooldown 1.5x)

### D(ML): price_cluster vol_atr_trend_min=1.0 실험 → DEAD PARAM 확정

- `paper_simulation.py` vol_atr_trend_min 1.2→1.0 실험:
  - **결과**: Sh=-0.93(↓-1.88!), PF=0.91(↓-0.42), Tr=22(↓-12), Consistency=0/8 → 치명적 악화
  - 원인: 임계값 낮춤 → 추세 억제 더 쉬워짐 → Trades 34→22 급감 → Sharpe 분산 폭발
- **vol_atr_trend_min 탐색 완전 종료**: 1.0(dead)/1.2(최적)/1.5+(Cycle355 이전 검증)
  - vol_atr_trend_min=1.2 확정 불변. 추가 실험 금지
- vol_atr_trend_min=1.2 복원 (변경 금지)
- `walk_forward.py` DEFAULT_GRIDS: dead param 주석 + 다음 방향(close_window=60) 명시

### F(리서치): price_cluster 남은 개선 방향 분석

- vol_atr_trend_min 방향 완전 소진 (1.0=dead 확정)
- PF=1.33 → 목표 1.5, gap=0.17 (binding constraint)
- **다음 방향**: close_window=60 실험 (현재 50, WFO 그리드에 이미 [50,60] 포함)

## 다음 사이클 (392) 핵심 과제

1. **B(리스크)**: `src/risk/circuit_breaker.py` recovery_window 또는 `drawdown_monitor.py` _update_regime 테스트
2. **D(ML)**: price_cluster close_window=60 paper_sim 실험
   - 설정: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2, "close_window": 60}`
3. **F(리서치)**: close_window=60 vs 50 신호 타이밍 차이 분석

## ⚠️ 중요 메모

- **price_cluster 파라미터**: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (변경 금지)
- **vol_atr_trend_min 탐색 완전 종료** (Cycle391 D 확정): 추가 vol_atr_trend_min 실험 금지
- **bounce_pct 탐색 완전 종료** (Cycle390 C 확정): 추가 bounce_pct 실험 금지
- **roc_ma_cross**: PASS 상태 유지 (Sh=1.81, Consist=4/8) — 파라미터 변경 금지
