# Current Cycle Briefing

_Last updated: 2026-07-02 (Cycle 383 완료)_

## 현재 상태

- **완료된 사이클**: 383
- **다음 사이클**: 384 (384 mod 5 = 4 → D+E+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Consist=4/8)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 383 주요 결과

### C(데이터): price_cluster bounce_pct=0.008 실험 — 혼재 결과
- `scripts/paper_simulation.py`: `bounce_pct=0.008` 실험 (더 민감한 bounce 탐지)
  - BTC 결과: Sharpe=1.21(+0.34↑), PF=1.27(+0.07↑), Trades=38(-3↓), Consistency=1/8(유지)
  - Sharpe 큰 개선이나 PF binding constraint 지속 → FAIL 유지
  - binding constraint: PF=1.27 < 1.5 (gap=0.23)
  - 결론: 방향 긍정적이나 PASS 달성 불충분 → 기본값(0.010) 복원
- paper_sim 파라미터 복원: `"price_cluster": {"vol_regime_filter": False}`

### B(리스크): transition_cushion None-confidence 테스트 추가
- `tests/test_risk_manager.py`: `test_regime_confidence_none_skips_cushion` 신규 추가
  - `transition_cushion_enabled=True` + `regime_confidence=None` → 포지션 미감소 검증
  - manager.py L594 `if regime_confidence is not None` 가드 정상 동작 확인
  - 306개 관련 테스트 통과 (총 8459개)

### F(리서치): roc_ma_cross EMA200 필터 분석 — 유지 확정
- BTC 1h 실데이터 EMA200 필터 품질 분석 (Cycle383 F):
  - 현재 신호 (EMA200 통과): 76개, 24h avg fwd return +0.329%, Win rate 60.5%
  - EMA200 차단 신호 (제거 시 추가): 13개, 24h avg fwd return -0.540%, Win rate 30.8%
  - **결론: EMA200 차단 신호 품질 낮음 (음수 fwd return, Win rate 절반) → 유지 확정**
  - EMA200 제거 탐색 방향 종료
  - walk_forward.py DEFAULT_GRIDS 주석에 분석 결과 반영

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC, bounce_pct=0.008 실험) | Sharpe=1.21, PF=1.27, Trades=38, Consist=1/8 FAIL |
| paper_sim (1h BTC, 복원 후) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14 avg, 4/8) |
| bundle_oos (4h BTC, CSV) | **5/5 PASS 유지** — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `scripts/paper_simulation.py` | bounce_pct=0.008 실험 + 결과 주석 + 기본값(0.010) 복원 (C) |
| `tests/test_risk_manager.py` | transition_cushion + None-confidence edge case 테스트 추가 (B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"] EMA200 분석 주석 추가 (F) |

## Cycle 384 예고 (384 mod 5 = 4 → D+E+F)

- **D(ML)**: price_cluster PF 개선 방향 탐색 (WFO 그리드 탐색 or 새 파라미터)
- **E(실행)**: WFO 그리드 dead param 정리 → IS 최적화 속도 개선 검토
- **F(리서치)**: roc_ma_cross FAIL 윈도우 특성 분석 (레짐 기반 접근 검토)
