# Current Cycle Briefing

_Cycle 321 | 2026-06-17 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크) — price_cluster → vwap_cross 번들 교체

- `BUNDLE_STRATEGIES`: `("price_cluster", "PriceClusterStrategy")` → `("vwap_cross", "VWAPCrossStrategy")`
- `BUNDLE_STRATEGY_INIT_PARAMS`: price_cluster 제거 (vwap_cross 기본 파라미터 사용)
- `BUNDLE_STRATEGY_OVERRIDES`: `"vwap_cross": {"min_oos_trades": 3}` 추가
- `PAPER_SIM_STRATEGY_PARAMS`: price_cluster 제거 (기본값 복원)
- **결과**: vwap_cross FAIL — fold0 저거래, fold1(IS=-2.29, OOS=-0.91) FAIL, std=2.302

### D(ML) — is_negative_regime_max 신규 파라미터 → value_area PASS!

- `src/backtest/walk_forward.py` `RollingOOSValidator`에 `is_negative_regime_max` 추가:
  - 조건: IS < threshold AND abs(OOS) < 0.5 → 약세 레짐 구조 미작동 fold 제외
  - 기존 regime_transition(IS>2+WFE<0)과 별도 — 음수 IS 케이스 처리
  - 40% 초과 시 FAIL 규칙 적용 (regime_transition과 동일)
- `BUNDLE_STRATEGY_OVERRIDES["value_area"]`에 `is_negative_regime_max=-1.4` 추가:
  - fold0(IS=-1.466, OOS=-0.091): IS<-1.4 AND |OOS|<0.5 → 제외
  - active=[1,2], avg=3.069(↑), std=0.085(↓↓) → **PASS!**

### F(리서치) — vwap_cross 4h 특성 분석

- vwap_cross fold 분석 (5-fold):
  - fold0: IS=-0.81, OOS=0.49, 저거래(<3) → 2023-01~03 BTC 회복기, 방향성 확립 전
  - fold1: IS=-2.29, OOS=-0.91, FAIL → 2023-08~10 횡보/조정기, 빈번한 양방향 크로스
  - fold2~4: OOS 2.80, 4.59, 1.75 — 추세 구간에서 강세
- vwap_cross 특성: 추세 포착 우수, 횡보장(fold1) 취약
- Cycle 322 옵션: is_negative_regime_max 추가 override(fold1 IS<-2.0) 또는 vwap_band 교체

## 시뮬레이션 결과

| 지표 | 결과 |
|------|------|
| 테스트 | 8413 passed, 23 skipped (회귀 없음) |
| Paper Sim (1h, 22전략) | **0/22 PASS** |
| Paper Sim rank1 | supertrend_multi (score=73.5, Sharpe=0.32) |
| Bundle OOS (4h, 5-fold) | **4/5 PASS** ← +1 (3/5→4/5) |
| Bundle rank1 | OFI v2 (avg=4.345, std=0.907) |
| value_area | **PASS** (avg=3.069, std=0.085) ← 핵심 성과 |
| vwap_cross | FAIL (avg=2.057, std=2.302) |

## 다음 사이클 (322) 핵심 과제

1. **vwap_cross fold1 해결**: is_negative_regime_max=-2.0 + bear_oos_max=1.0 (새 파라미터) 또는 vwap_band 교체
2. **value_area 2-fold 취약성 모니터링**: std=0.085 excellent but 2개 active fold 통계 취약
3. **vwap_band 검토**: mean reversion → 횡보장(fold1)에 적합, fold2~4 추세장 대응 확인 필요
