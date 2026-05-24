# Current Cycle Briefing

_Updated: 2026-05-24 — Cycle 202 완료 (B+D+F)_

## 현재 상태

| 항목 | 값 |
|------|-----|
| 완료 사이클 | Cycle 202 |
| 다음 사이클 | Cycle 203 |
| 카테고리 | C(데이터) + B(리스크) + F(리서치) |
| 테스트 수 | 7801 passed, 23 skipped |
| PASS 전략 수 | 22개 (QUALITY_AUDIT.csv) |
| SIM 결과 | 0/5 Bundle OOS PASS, 0/22 Paper SIM PASS (합성 데이터) |

## Cycle 202 변경 요약

### D1 개선: WalkForwardOptimizer IS 전체 음수 진단
- `src/backtest/walk_forward.py`: `run()` 내 avg IS Sharpe < -0.5 시 fail_reasons 추가
- `"IS 전체 음수: avg IS Sharpe=X.XXX — 전략 미작동 또는 합성 데이터(GBM)"` 메시지
- GBM 합성 데이터에서 cmf/wick_reversal/elder_impulse IS 전부 음수 패턴 자동 진단

### D2 개선: RegimeAwareFeatureBuilder.get_feature_importance()
- `src/ml/features.py`: RF 50트리 빠른 fit으로 레짐별 피처 중요도 dict 반환
- 사용법: `builder.get_feature_importance(df, regime="bull")` → `{feature: importance}`
- 합성 데이터 vs 실데이터 피처 중요도 비교에 활용 예정

### B1 검증: KellySizer ATR low 케이스 테스트
- `tests/test_kelly_sizer_regime_edge_cases.py`: `test_atr_low_does_not_expand_size` 추가
- ATR 낮을 때 포지션 확대 없음 (min(target_atr/atr, 1.0) = 1.0) 의도적 보수적 설계 검증

### 테스트 +6개
- `test_all_is_sharpe_negative_adds_fail_reason` (walk_forward)
- `TestGetFeatureImportance.*` 4개 (feature_builder)
- `test_atr_low_does_not_expand_size` (kelly_sizer)

## SIM 결과 주요 패턴 (Cycle 202)

- Paper SIM 1h (합성, GBM): 0/22 PASS — GBM 한계, 결과 Cycle 201과 동일
  - price_action_momentum: avg Sharpe=6.90, +52.22% (합성 과적합)
  - cmf: avg Sharpe=5.99, +46.21% (합성 과적합)
  - value_area: avg 6 trades, Consistency 0/8 → 신호 조건 여전히 엄격
- Bundle OOS 4h (합성): 0/5 PASS — IS 전부 음수 (새 fail_reason으로 진단됨)
  - elder_impulse fold 1: OOS Sharpe=3.794 (반복 패턴, GBM 특정 구간)
  - wick_reversal fold 8: OOS PF=1.141 < 1.5 기준 미달

## 다음 사이클 우선순위 (Cycle 203, 203 mod 5 = 3)

**C(데이터) + B(리스크) + F(리서치)**

1. **C(데이터)**: DataFeed retry/fallback 파라미터 점검, OrderFlowAnalyzer VPIN 정확도
2. **B(리스크)**: DrawdownMonitor streak cooldown 만료 후 size 복원 동작 문서화
3. **F(리서치)**: get_feature_importance() 활용하여 합성 vs 실데이터 피처 중요도 비교 계획
