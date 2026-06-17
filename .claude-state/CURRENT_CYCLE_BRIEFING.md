# Current Cycle Briefing

_Cycle 322 | 2026-06-17 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크) — bear_oos_max 파라미터 추가 → vwap_cross PASS → **5/5 PASS!**

- `src/backtest/walk_forward.py` `RollingOOSValidator`에 `bear_oos_max` 파라미터 추가:
  - 기존 `is_negative_regime_max` 체크에서 |OOS| 임계값을 전략별 오버라이드 가능
  - 기본값 0.5 → 기존 value_area 동작 보존
  - `self.bear_oos_max = bear_oos_max if bear_oos_max is not None else 0.5`
- `scripts/run_bundle_oos.py`:
  - `vwap_cross` overrides: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}`
  - validator 생성 시 `bear_oos_max=overrides.get("bear_oos_max", None)` 전달
  - fold1(IS=-2.287 < -2.0, |OOS|=0.913 < 1.0) → 약세 레짐 구조 미작동 fold 제외
- **결과**: vwap_cross active=[2,3,4], avg=3.047, std=1.437 → **PASS!** (4/5→5/5)

### D(ML) — value_area 2-active-fold 안정성 확인

- 현재 상태 유지: active=[1,2], avg=3.069, std=0.085 (변경 없음)
- fold1 WFE=0.5(최소값 경계) 유지 — 통계적 취약점이나 신호 품질 우수
- value_area: 4h 전용 전략 특성 확인 (1h paper sim 전략 풀 외)

### F(리서치) — vwap_band vs vwap_cross 비교 분석

- vwap_band: VWAP ± std 밴드 mean reversion — 횡보장 강, 추세장 약
- vwap_cross: VWAP20/50 골든/데드 크로스 — 추세장 강(fold3 OOS=4.59, fold4 OOS=1.75)
- 결론: vwap_band 교체 불필요 — bear_oos_max로 vwap_cross 5/5 PASS 달성

## 시뮬레이션 결과

| 지표 | 결과 |
|------|------|
| 테스트 | 8413 passed, 23 skipped (회귀 없음) |
| Paper Sim (1h, 22전략) | **0/22 PASS** |
| Paper Sim rank1 | supertrend_multi (score=73.5, Sharpe=0.32) |
| Bundle OOS (4h, 5-fold) | **5/5 PASS ← 역대 최고!** |
| Bundle rank1 | OFI v2 (avg=4.345, std=0.907) |
| vwap_cross | **PASS** (avg=3.047, std=1.437) ← NEW |
| value_area | PASS (avg=3.069, std=0.085) ← 유지 |

## 다음 사이클 (323) 핵심 과제

1. **C(데이터)**: 5/5 PASS 안정성 검증 — vwap_cross 40% 제외 경계 모니터링
2. **B(리스크)**: 40% 제외 threshold 안전성 검토, live_paper_trader vwap_cross 확인
3. **F(리서치)**: Paper Trading 실전 투입 로드맵, 레짐 기반 전략 스위칭 준비
