# Current Cycle Briefing

_Last updated: 2026-07-01 (Cycle 378 완료)_

## 현재 상태

- **완료된 사이클**: 378
- **다음 사이클**: 379 (379 mod 5 = 4 → D+E+F)
- **연속 PASS 실패**: 63연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 378 주요 결과

### C(데이터): high_conf_only dead param 확정
- `src/strategy/price_cluster.py`: `high_conf_only=False` 파라미터 + MEDIUM confidence 억제 로직 추가
- 실험 결과: Sh=0.60(-0.05 악화), PF=1.15(-0.03 악화), Trades=36(-6), Consistency=0/8(-1)
- W6 PASS 윈도우(PF=2.01) → FAIL(PF=1.48 < 1.5): 가장 좋은 윈도우에서도 악화
- **결론**: HIGH/MEDIUM confidence 분류가 bounce 수익성 예측 불가. dead param 확정.

### B(리스크): MIN_TRADES_FOR_KELLY 10→15
- `src/risk/kelly_sizer.py`: `MIN_TRADES_FOR_KELLY = 10` → `15`
- 근거: paper_sim min_trades=15 기준과 정렬 — n<15이면 backtest FAIL이지만 Kelly는 더 관대했던 불일치 해소
- 영향: trades=10~14 전략은 win_rate가 50%로 더 강하게 수축됨 (shrink_factor 0.40~0.48)
- dema_cross(26 trades), price_cluster(41 trades) — 현행 전략 영향 없음

### F(리서치): 63연속 PASS 실패 구조적 원인 확정
- PF=1.5 목표는 1h BTC 전략의 구조적 상한선
- 수수료 드래그: 0.11% × 26 평균 거래 = 2.86% 누적 비용
- dema_cross: avg PF=1.38 (gap=0.12), price_cluster: avg PF=1.20 (gap=0.30)
- MC_P_THRESHOLD=0.10 이미 완화됨 (Cycle296에서 0.05→0.10)
- WF 설계(50% pass_ratio, 8 window) 자체는 병목이 아님

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC) | 0/19 PASS (63연속 실패) — dema_cross Sh=0.85, PF=1.38 |
| bundle_oos (4h BTC) | 5/5 PASS 유지 — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/price_cluster.py` | `high_conf_only=False` 파라미터 + 필터 로직 (C) |
| `src/backtest/walk_forward.py` | dead param 주석 + 그리드에서 high_conf_only 제거 (C) |
| `src/risk/kelly_sizer.py` | `MIN_TRADES_FOR_KELLY` 10→15 (B) |
| `scripts/paper_simulation.py` | high_conf_only 실험 문서화 주석 (C) |

## Cycle 379 예고 (379 mod 5 = 4 → D+E+F)

- **D(ML)**: roc_ma_cross `volume_filter` 파라미터 탐색
- **E(실행)**: PaperConnector slippage 검증 (실제 슬리피지 vs 가정 0.05%)
- **F(리서치)**: price_cluster PF 개선 — `min_cluster_strength_ratio` 또는 `confirmation_bars` 탐색
