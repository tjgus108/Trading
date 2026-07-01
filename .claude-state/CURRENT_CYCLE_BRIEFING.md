# Current Cycle Briefing

_Last updated: 2026-07-01 (Cycle 377 완료)_

## 현재 상태

- **완료된 사이클**: 377
- **다음 사이클**: 378 (378 mod 5 = 3 → C+B+F)
- **연속 PASS 실패**: 62연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 377 주요 결과

### B(리스크): 인프라 재검토
- DrawdownMonitor 직렬화 검토: Cycle357 이후 안정적. 변경 불필요
- KellySizer Half-Kelly=6.9% < max_fraction=10% → 현 설정 유지
- circuit_breaker.py 파라미터: BTC 1h 실증 기반 설정 유지

### D(ML): EMA200 BUY 필터 실험 → dead param 확정
- `src/data/feed.py` `_add_indicators()`: ema200 피처 추가 (인프라)
- `scripts/paper_simulation.py` `enrich_indicators()`: ema200 동기화 (feed.py 미러)
- `src/strategy/dema_cross.py`: `ema200_filter=False` 파라미터 + close < ema200 → HOLD 로직
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["dema_cross"]에 `ema200_filter=[False,True]` 추가
- **실험 결과**: ema200_filter=True → Sh=0.56(-34%), PF=1.34, Trades=22 (vs 기존 Sh=0.85, PF=1.38, T=26)
- **원인 분석**: 2023초 BTC EMA200 미만 회복 구간 진입 차단 + 200봉 워밍업 필요
- **결론**: **dead param 확정**. ema200_filter=False 복원. dema_cross 탐색 완전 종료

### F(리서치): dema_cross 탐색 완전 종료 선언
- 모든 파라미터 방향 소진: fast/slow, rsi_dir_filter, rsi_dir_threshold, bb_width_min_filter,
  dist_pct_min, ema_slope, macd_hist, SL, TP, ema200_filter
- **결론**: PF=1.38 → 목표 1.50 (gap=0.12) 달성 불가. dema_cross 최적화 완전 종료
- 향후: price_cluster 또는 roc_ma_cross 개선 전략으로 전환

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/data/feed.py` | ema200 피처 추가 (D) |
| `scripts/paper_simulation.py` | ema200 동기화 + ema200_filter 실험→복원+주석 (D) |
| `src/strategy/dema_cross.py` | ema200_filter=False 파라미터 + 필터 로직 (D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] ema200_filter=[False,True] 추가 (D) |

## Cycle 378 예고 (378 mod 5 = 3 → C+B+F)

- **C(데이터)**: price_cluster 또는 roc_ma_cross 새 파라미터 탐색 (dema_cross 종료 후 전략 전환)
- **B(리스크)**: KellySizer Bayesian shrinkage 계수 세밀화 분석
- **F(리서치)**: 62연속 PASS 부재 원인 분석 (WF 설계 vs 전략 파라미터 한계)
