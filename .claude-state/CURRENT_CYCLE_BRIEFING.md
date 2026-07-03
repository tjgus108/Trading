# Current Cycle Briefing

_Last updated: 2026-07-03 (Cycle 390 완료)_

## 현재 상태

- **완료된 사이클**: 390
- **다음 사이클**: 391 (391 mod 5 = 1 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)
- **전체 테스트 수**: 8497개 (+1 집계 기준, 실 추가 5개)

## Cycle 390 주요 결과

### A(품질): optimize_roc_ma_cross 헬퍼 + volume_filter 파라미터 테스트 5개 추가

- `tests/test_phase_d.py`: optimize_roc_ma_cross 헬퍼 3개 (helper, single_window, result_fields)
- `tests/test_roc_ma_cross.py`: volume_filter 파라미터 2개 (저거래량 차단, 고거래량 허용)

### C(데이터): price_cluster bounce_pct=0.004 실험 → dead param 확정

- `paper_simulation.py` bounce_pct 0.006→0.004 실험:
  - **결과**: Sh=0.66(↓-0.29), PF=1.27(↓-0.06), Tr=27(↓-7) → 역효과
  - 패턴: bounce_pct↓ = entry zone 좁아짐 → trades 감소 + signal quality 저하
- **bounce_pct 탐색 완전 종료**: 0.010→0.008→0.006→0.004 전부 검증
  - 0.006(filter=T) 최적 확정. 추가 bounce_pct 실험 금지
- bounce_pct=0.006 복원 (변경 금지)
- `walk_forward.py` DEFAULT_GRIDS price_cluster: bounce_pct=[0.006,...] + 탐색 종료 주석

### F(리서치): price_cluster PF 개선 경로 분석

- 코드 로직 확인: threshold = cluster_low × bounce_pct (↓일수록 entry zone 좁아짐)
- NEXT_STEPS의 "bounce_pct 하향 → Tr 증가" 예측이 코드 로직과 반대임을 확인
  - 실측 데이터로 검증: 0.010(41)→0.008(38)→0.006(34)→0.004(27) 일관 감소
- **결론**: bounce_pct 방향 완전 소진. 새 개선 방향: vol_atr_trend_min 탐색

## 다음 사이클 (391) 핵심 과제

1. **B(리스크)**: `src/risk/circuit_breaker.py` 또는 `drawdown_monitor.py` 미커버 기능 테스트
2. **D(ML)**: price_cluster vol_atr_trend_min=1.0 실험 (`{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.0}`)
   - 현재 1.2가 Tr=34 억제 → 1.0으로 완화 시 Tr=40+ 기대
3. **F(리서치)**: price_cluster FAIL 윈도우 패턴 분석 (어느 period에 FAIL 집중?)
   - vol_atr_trend_min이 신호를 얼마나 억제하는지 확인

## ⚠️ 중요 메모

- **price_cluster 파라미터**: `{"vol_regime_filter": True, "bounce_pct": 0.006, "vol_atr_trend_min": 1.2}` (변경 금지)
- **bounce_pct 탐색 완전 종료** (Cycle390 C 확정): 추가 bounce_pct 실험 금지
- **roc_ma_cross**: PASS 상태 유지 (Sh=1.81, Consist=4/8) — 파라미터 변경 금지
