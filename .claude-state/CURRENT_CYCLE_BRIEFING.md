# Current Cycle Briefing

_Last updated: 2026-06-30 (Cycle 370 완료)_

## 현재 상태

- **완료된 사이클**: 370
- **다음 사이클**: 371 (371 mod 5 = 1 → B+D+F)
- **연속 PASS 실패**: 55연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 370 주요 결과

### A(품질): dema_cross thr=40 WFO 검증
- WFO best_params: thr=45 (3/3 윈도우), thr=40 한 번도 선택 안 됨
- is_stable=False, oos_sharpe_std=2.6152 (trades 6/7/20 저거래)
- **결론**: paper_sim Sh=0.80(rank1)은 일회성 가능성 → Cycle371에서 thr=45 재실험 예정

### C(데이터): dist_pct_min=0.003 실험
- Sh=-0.35, Trades=15 → 기존(Sh=0.80, Trades=30) 대비 **역효과**
- dist_pct_min=0.002 유지 확정, 탐색 종료

### F(리서치): roc_period=15 실험
- Sh=-0.33 → roc_period=12(Sh=0.34) 대비 악화
- roc_period 탐색 완료 (10/12/15), roc_period=12 최적 확정

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/dema_cross.py` | dist_pct_min 파라미터 추가 (기본=0.002) |
| `src/backtest/walk_forward.py` | optimize_dema_cross() factory + 주석 업데이트 |
| `scripts/paper_simulation.py` | 실험 후 복원 (C+F) |

## Cycle 371 예고

- **B(리스크)**: dema_cross thr=45 재실험 (WFO 결과 기반 재검증)
- **D(ML)**: frama atr_period 탐색 (현재 rank2, Sh=0.24 개선)
- **F(리서치)**: dema_cross 추가 개선 방향 분석
