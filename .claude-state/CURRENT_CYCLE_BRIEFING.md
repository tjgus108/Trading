# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 391 완료)_

## 현재 상태

- **완료된 사이클**: 391
- **다음 사이클**: 392 (392 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8507개 (+10)

## Cycle 391 주요 결과

### B(리스크): circuit_breaker max_daily_trades 경계값 + drawdown_monitor 레짐 테스트 6개

- `tests/test_circuit_breaker.py`: max_daily_trades 경계값 4개 (at_limit, one_below, reset_daily, zero_unlimited)
- `tests/test_drawdown_monitor.py`: set_regime + set_ranging_macro_neutral 2개

### D(ML): vol_atr_trend_min=1.0 실험 → dead param 확정

- `paper_simulation.py` vol_atr_trend_min 1.2→1.0 실험:
  - **결과**: Sh=-0.93(↓-1.88), PF=0.91(↓-0.42), Tr=22(↓-12), 0/8 FAIL
  - 역효과: 낮은 임계값=더 강한 필터링=더 적은 거래 (방향 오인)
- **확정**: 1.0 하향 방향 종료. 1.2 복원 (변경 금지)
- `walk_forward.py` DEFAULT_GRIDS 주석 업데이트

### F(리서치): vol_atr_trend_min 방향성 분석

- 코드 로직: ATR/ATR_MA > vol_atr_trend_min 시 신호 차단
- 낮은 임계값 → 더 강한 필터링 → 더 적은 거래 (완화 방향이 반대였음)
- **올바른 완화 방향**: 임계값 상향 (1.5+) → 덜 필터링 → 더 많은 거래
- 다음 실험: vol_atr_trend_min=1.5 (Cycle 392 D 예정)

## 다음 사이클 (392) 핵심 과제

1. **B(리스크)**: 추가 미커버 기능 테스트 (circuit_breaker 또는 drawdown_monitor)
2. **D(ML)**: vol_atr_trend_min=1.5 상향 실험
   - `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.5}`
   - 기대: 1.2(Tr=34)보다 더 많은 거래 (Tr=38+?) 유지하면서 PF↑ 또는 유지
3. **F(리서치)**: price_cluster vol_atr_trend_min=1.5 vs 1.2 FAIL 윈도우 비교 분석
   - 어느 윈도우에서 추가 거래가 발생하고, 어느 윈도우에서 quality 저하?

## ⚠️ 중요 메모

- **price_cluster 파라미터**: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (복원 완료, 변경 금지)
- **vol_atr_trend_min 탐색 방향**: 하향(1.0) 종료, 상향(1.5+)만 탐색
- **bounce_pct 탐색 완전 종료** (Cycle390 C 확정): 추가 bounce_pct 실험 금지
- **roc_ma_cross**: PASS 상태 유지 (Sh=1.81, Consist=4/8) — 파라미터 변경 금지
