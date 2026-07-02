# Current Cycle Briefing

_Last updated: 2026-07-02 (Cycle 381 완료)_

## 현재 상태

- **완료된 사이클**: 381
- **다음 사이클**: 382 (382 mod 5 = 2 → B+D+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross 유지 — Sh=1.81, PF=2.02, Trades=14 avg)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 381 주요 결과

### B(리스크): KellySizer MIN_TRADES_FOR_KELLY=15 경계 테스트
- `src/risk/kelly_sizer.py`: docstring 버그 수정 — MIN_TRADES_FOR_KELLY=10 → 15
  - 클래스 상수(line 456)는 이미 15 — docstring만 잘못 표기됨
- `tests/test_kelly_integration.py`: 경계 테스트 추가
  - `test_min_trades_kelly_boundary_14_vs_15`: n=14 shrinkage 적용, n=15 raw win_rate
  - qty_14 ≤ qty_15 검증 (소표본 방어 정상 동작 확인)

### D(ML): price_cluster atr_bounce_factor=1.0 실험 — 혼재 결과
- `scripts/paper_simulation.py`: `atr_bounce_factor=1.0` 실험
- 실험 결과: **Sharpe=1.17(+0.30↑), PF=1.25(+0.05↑), Trades=44, Consistency=1/8(-1)**
  - Sharpe avg 개선(0.87→1.17)이나 Consistency 악화(2/8→1/8) → FAIL 유지
  - Binding constraint: PF 1.25 < 1.5
- **결론**: 기본값(0.0) 복원. atr_bounce_factor WFO 탐색은 DEFAULT_GRIDS에 추가 유지

### F(리서치): roc_ma_cross 4h OOS 검증 — 신호 희소 확정
- 4h WFO 분석 (BTC 4h CSV 리샘플링): **1-3 trades/window** (min_trades=8 미달)
- volume_filter=True + EMA50 조건이 4h에서 너무 제한적
- **결론**: roc_ma_cross 4h 번들 추가 불가. 1h only 전략으로 분류
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["price_cluster"] atr_bounce_factor=[0.0, 1.0] 추가

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14 avg, 4/8) |
| bundle_oos (4h BTC) | 5/5 PASS 유지 — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/risk/kelly_sizer.py` | docstring 수정: MIN_TRADES_FOR_KELLY=10 → 15 (B) |
| `tests/test_kelly_integration.py` | boundary test 추가: qty_14 ≤ qty_15 (B) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["price_cluster"] atr_bounce_factor=[0.0, 1.0] (D) |
| `scripts/paper_simulation.py` | atr_bounce_factor=1.0 실험 결과 주석 + 기본값 복원 (D) |

## Cycle 382 예고 (382 mod 5 = 2 → B+D+F)

- **B(리스크)**: DrawdownMonitor transition_cushion 파라미터 검토 또는 roc_ma_cross Trades 증가 (vol_ratio_min=1.1)
- **D(ML)**: price_cluster bounce_pct=0.008 실험 (Trades↑ 가설) 또는 roc_ma_cross vol_ratio_min=1.1
- **F(리서치)**: roc_ma_cross 4h용 별도 파라미터 세트 연구 (volume_filter=False, roc_period=6)
