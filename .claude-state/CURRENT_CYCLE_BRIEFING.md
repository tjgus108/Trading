======================================================================
🔄 CYCLE 232 — 2026-05-28
======================================================================

## 이번 사이클 배정 카테고리

### [B] Risk Management
- **Focus**: KellySizer 레짐별 동적 fraction
- **완료**: _REGIME_FRACTION 딕셔너리, get_dynamic_fraction(), update_fraction_for_regime()
- **테스트**: 11개 신규 (TestKellySizerDynamicFraction)

### [D] ML & Signals
- **Focus**: VPIN 피처 + OFI 통합 + walk_forward 안정성
- **완료**: vpin_50 피처 (FeatureBuilder), Sharpe IC 파라미터 선택 (walk_forward.py)
- **테스트**: 5개 신규 (TestFeatureBuilderVPIN) + 피처 카운트 7개 업데이트

### [SIM] 시뮬레이션
- Paper: 0/22 PASS (합성 데이터 한계, 최고 price_action_momentum +49%)
- OOS: 0/5 PASS (Sharpe std 3.4~6.4, narrow_range 3/9 fold 최선)

### [F] Research
- Sharpe IC: avg - 0.5*std로 안정적 파라미터 선택 → walk_forward.py 적용
- VPIN: Easley et al. 2012, 플래시 크래시 선행 지표, ML 피처 활용
- OOS Sharpe std 원인: 레짐 이질성 (IS/OOS 불일치)

## 버그 수정
- `BinanceWebSocketFeed.__init__`: stale_timeout=0 전달 시 5400 저장 버그 수정

## 테스트 현황
- 8,101 passed, 23 skipped (Cycle 231: 7,955 → +146)

## 다음 사이클
- 233 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)
- 핵심: OFI/VPIN 상관성 분석, DrawdownMonitor+KellySizer 통합, Sharpe IC 효과 측정
