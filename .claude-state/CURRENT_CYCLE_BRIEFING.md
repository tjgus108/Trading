# Current Cycle Briefing

_Last updated: 2026-07-02 (Cycle 382 완료)_

## 현재 상태

- **완료된 사이클**: 382
- **다음 사이클**: 383 (383 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — vol_ratio_min=1.2 복원)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 382 주요 결과

### B(리스크): vol_ratio_min=1.1 실험 — FAIL, 1.2 최종 확정
- `scripts/paper_simulation.py`: `vol_ratio_min=1.1` 실험 → 역효과 확정
  - BTC 결과: Sharpe=1.51(-0.30↓), PF=1.87(-0.15↓), Trades=16(+2↑), Consistency=2/8(-2↓)
  - FAIL 원인: `sharpe 0.32 < 1.0 (x1), profit_factor 1.11 < 1.5 (x1)` — 노이즈 신호 포함
  - vol_ratio_min 탐색 완전 종료: 1.0, 1.1, 1.2, 1.5 모두 검증 → 1.2 최적 확정
- paper_sim 파라미터 복원: `vol_ratio_min=1.2` (PASS 재확인)

### D(ML): price_cluster bounce_pct=0.008 DEFAULT_GRIDS 추가
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["price_cluster"]["bounce_pct"]에 0.008 추가
  - 기존: [0.010, 0.020, 0.025] → 신규: [0.008, 0.010, 0.020, 0.025]
  - WFO 탐색에서 더 민감한 bounce 탐지 옵션 추가 (IS 구간 실험 가능)

### F(리서치): roc_ma_cross 4h 분석 — 1h only 최종 확정
- 4h OOS 구조 분석 (RollingOOSValidator: oos=360 4h봉 = 2개월):
  - 1h: 1440봉 test window → avg 14-16 trades
  - 4h: 360봉 (동일 2개월) → 예상 3-7 trades (volume_filter 유무 무관)
  - **결론: roc_ma_cross 4h 번들 추가 구조적으로 불가**
  - 근본 원인: 2개월 4h window에서 ROC + EMA50/200 조건 동시 충족 횟수 < 8
  - roc_ma_cross 1h only 전략 최종 분류 (변경 불필요)

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC, vol=1.1 실험) | **0/19 FAIL** (roc_ma_cross Sh=1.51, PF=1.87, Trades=16, Consist=2/8) |
| paper_sim (1h BTC, vol=1.2 복원) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14 avg, 4/8) |
| bundle_oos (4h BTC, CSV) | **5/5 PASS 유지** — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `scripts/paper_simulation.py` | vol_ratio_min=1.1 실험 + 결과 주석 + 1.2 복원 (B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["price_cluster"]["bounce_pct"] 0.008 추가 (D) |

## Cycle 383 예고 (383 mod 5 = 3 → C+B+F)

- **C(데이터)**: price_cluster bounce_pct=0.008 paper_sim 직접 테스트 (WFO 탐색 보완)
- **B(리스크)**: DrawdownMonitor transition_cushion 파라미터 검토 또는 roc_ma_cross 신호 품질 분석
- **F(리서치)**: roc_ma_cross PASS 4/8 → 더 안정적인 5/8+ PASS 조건 연구
