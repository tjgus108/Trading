======================================================================
🔄 CYCLE 248 — 2026-05-30
======================================================================

## 이번 사이클 배정 카테고리

248 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)

## 핵심 작업 완료

### [C] generate_synthetic_data() regime 파라미터 개선
- 목표: IS Sharpe 음수 (elder_impulse/narrow_range 100%) 근본 해소
- 수정 (run_bundle_oos.py):
  - P(bull→bear): 0.02 → 0.01 (bull 평균 100 bars, bull 비율 ~80%)
  - P(bear→bull): 0.03 → 0.04 (bear 평균 25 bars, 빠른 회복)
  - drift: ±0.02% → ±0.03% per bar (추세 신호 강도 1.5x)
- 결과: IS Sharpe 음수 비율 개선 미완 (elder 100%, narrow 100% 지속)
- 결론: GBM 기반 합성 데이터 자체 한계 → 실거래소 데이터 필요

### [B] regime=None + MDD=9% 복합 축소 테스트 추가
- 신규: TestKellyDrawdownIntegration::test_regime_none_mdd9_compound
- 검증: regime=None(Kelly 레짐 스케일 없음) × mdd_warn(0.5) × kelly_frac(0.5) = 0.25x
- 8340 passed (신규 1개)

### [F] value_area --min-trades 5 완화 검증
- 결과: 0/5 PASS (value_area 포함 전 전략 FAIL)
- 원인: 56% fold에서 4~5 trades (신호 부족), IS Sharpe 78% 음수
- 결론: min-trades 완화 효과 없음 (실거래소 데이터 필요)

## 시뮬레이션 결과

### Bundle OOS BTC 4h (--min-trades 5, 합성)
- 0/5 PASS
- Rank #1: cmf (Score 79.9, OOS Sharpe -1.473, Avg Trades 12.4, OOS MDD 7.64%)
- Rank #2: elder_impulse (50.9), #3: wick_reversal (49.2)
- IS Sharpe 음수: elder/narrow 100%, cmf/wick 89%, value_area 78%

### Paper SIM BTC 1h (이전 Cycle 247 결과 유지)
- 0/22 PASS
- Composite #1: value_area (Score 73.9, AvgSharpe 4.39, AvgTrades 27, AvgMDD 3.1%)

## 테스트
8340 passed, 23 skipped (신규 1개 test_regime_none_mdd9_compound)

## 다음 사이클: 249 (D+E+F)
- D: quality_audit.make_synthetic_data() → Bundle OOS fallback 교체 검토
- E: Paper Trading slippage 모델 및 TWAP executor 검증
- F: cmf 전략 우위 분석 (Bundle OOS Rank #1 지속)
