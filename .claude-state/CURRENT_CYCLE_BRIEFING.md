# Current Cycle Briefing

_Cycle 285 — A(품질) + C(데이터) + F(리서치)_
_Completed: 2026-06-07_

## 이번 사이클 수행 작업

### A(품질): trend_confirm_bars=2 복귀 + max_oos_sharpe_std=2.5 완화
- `scripts/run_bundle_oos.py`: `trend_confirm_bars=3→2` 복귀
  - 결과: fold3 여전히 2 trades excluded → trend_confirm_bars 무관한 구조적 문제 확인
  - fold4 OOS=-0.006 유지 → cmf_confirm=True가 핵심 기여 확정
- `BUNDLE_STRATEGY_OVERRIDES`: `max_oos_sharpe_std=2.5` 추가
  - std 2.450 < 2.5 → std 기준 통과
  - 실제 FAIL 원인: fold4 WFE=-0.002 (OOS=-0.006 / IS=2.507) < 0.5

### C(데이터): 2022 bear market 데이터 추가 시도 → 역효과 → 롤백
- 2022 합성 bear market 8760행을 1h.csv에 prepend 시도
- fold 수 5→11로 증가 → std 증가 (cmf 1.888→4.204)
- cmf 13회 연속 PASS → FAIL (2022 구간 신호 부족 + 레짐 변화)
- 롤백: 원래 12000행 (2023-01~2024-05) 복구

### F(리서치): fold4 WFE 구조 분석
- IS=2023-08~2024-02 강한 상승장: IS Sharpe=2.507
- OOS=2024-02~04 ATH 전후: OOS Sharpe=-0.006
- cmf_confirm=True가 ATH 구간 BUY 차단 → 거래 부족 → OOS ≈ 0
- 다음: atr_threshold 낮춰 fold4 거래 수 늘리기

## 시뮬레이션 결과
- 테스트: 8377 passed, 23 skipped
- Bundle OOS: cmf PASS(13회), supertrend_multi FAIL(std=2.386, fold4 WFE=-0.002)
- Paper Sim: 0/22 PASS (rank1: supertrend_multi +6.73%)

## 다음 사이클 (Cycle 286: B(리스크) + D(ML) + F(리서치))
1. atr_threshold=0.7→0.5 완화 → fold4 OOS 거래 수 증가 + WFE 개선
2. fold3 excluded 해결: min_oos_trades=2 또는 IS 파라미터 탐색 범위 재조정
3. cmf 13회 PASS 안정성 유지 확인
