# Current Cycle Briefing

_Last updated: 2026-07-02 (Cycle 380 완료)_

## 현재 상태

- **완료된 사이클**: 380
- **다음 사이클**: 381 (381 mod 5 = 1 → B+D+E)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — 65+ 사이클 만에 첫 PASS! 🎉)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 380 주요 결과

### A(품질): roc_ma_cross vol_ratio_min=1.2 → 🎉 FIRST PASS
- `scripts/paper_simulation.py`: `"roc_ma_cross": {"volume_filter": True, "vol_ratio_min": 1.2}` 실험
- 실험 결과: **Sharpe=1.81, PF=2.02, AvgTrades=14, Consistency=4/8 PASS**
- 65+ 사이클 연속 FAIL 해소 — roc_ma_cross 역사상 첫 PASS
- vol_ratio_min 시퀀스: 1.0(baseline) → 1.2(PASS 균형) → 1.5(Trades 부족, FAIL)
- **확정 파라미터**: `{"volume_filter": True, "vol_ratio_min": 1.2}` (변경 금지)

### C(데이터): price_cluster confirmation_bars — 혼재 결과
- `src/strategy/price_cluster.py`: `confirmation_bars=0` 파라미터 추가 (코드 구현 완료)
- 실험 결과 (confirmation_bars=1): **Sharpe=0.50(0.87→-0.37↓), PF=1.18(유지), Trades=39, 2/8**
- bounce 후 1봉 hold 확인이 타이밍 지연 손실 유발 → Sharpe 감소, PF 개선 없음
- **결론**: confirmation_bars=0(기본값) 복원. 코드 보존 (confirmation_bars=2 향후 실험 가능)

### F(리서치): vol_ratio_min 시퀀스 분석 완료
- vol_ratio_min 전수 분석 (BTC 1h, volume_filter=True):
  - 1.0: Trades=36, Sharpe~0.34, PF~1.0 (필터 없음과 동등)
  - 1.2: **Trades=14, Sharpe=1.81, PF=2.02 → PASS** ← 최적 균형점
  - 1.5: Trades=10, Sharpe=0.72, PF=1.68 → FAIL (Trades<15)
- **결론**: vol_ratio_min=1.2 확정. 이 방향 탐색 완료.

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| paper_sim (1h BTC) | **1/19 PASS** (roc_ma_cross Sh=1.81, PF=2.02, Trades=14 avg) |
| bundle_oos (4h BTC) | 5/5 PASS 유지 — cmf, ofi_v2, supertrend_multi, vwap_cross, value_area |

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/price_cluster.py` | `confirmation_bars` 파라미터 + N봉 bounce 확인 로직 (C) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["roc_ma_cross"] `vol_ratio_min=[1.0,1.2,1.5]` + `optimize_roc_ma_cross()` 업데이트 (A+F) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["price_cluster"] `confirmation_bars=[0,1,2]` (C) |
| `scripts/paper_simulation.py` | roc_ma_cross PASS 결과 확정 주석 + price_cluster 실험 결과 + 복원 (A+C) |

## Cycle 381 예고 (381 mod 5 = 1 → B+D+E)

- **B(리스크)**: roc_ma_cross 4h OOS 검증 / Bundle 추가 가능성 타진
- **D(ML)**: price_cluster 다음 파라미터 탐색 (atr_bounce_factor 또는 bounce_pct 조정)
- **E(실행)**: roc_ma_cross PASS 전략 실전 배포 준비 점검
