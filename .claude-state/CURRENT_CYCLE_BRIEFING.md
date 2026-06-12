# Current Cycle Briefing

_Cycle 304 완료 — 2026-06-12_

## 완료된 작업

### D(ML) — bounce_pct=0.030 단독 실험 → 역효과
- `scripts/paper_simulation.py`: bounce_pct 0.025→0.030 실험
- 결과: Sharpe 3.76→**0.53** (급락), trades 12→50 (과도 증가)
- **결론**: 진입 장벽 완화 시 false signal 급증. 0.025 확정, bounce_pct 탐색 완료

### D(ML) — walk_forward close_window 그리드 업데이트
- `src/backtest/walk_forward.py`: close_window [40,50] → [50,60]
- close_window=40 역효과(Cycle303) 실증 → 40 제거, 60 탐색 추가

### F(리서치) — narrow_range ATR/ATR_MA 고변동성 억제 필터
- `src/strategy/narrow_range.py`: TREND_REGIME_MAX=1.4 필터 추가
- ATR/ATR_MA(20) > 1.4 시 NR 신호 억제 (Bundle OOS fold1/4 FAIL 저감 목적)
- 기본값 trend_regime_max=0.0 (비활성), 파라미터로 활성화

### E(실행) — adaptive_slippage 유지 확인
- engine.py adaptive_slippage=True (Cycle299 이후 지속)

## 시뮬레이션 결과

| 시뮬 | 결과 |
|------|------|
| Paper Sim BTC 1h | 0/22 PASS (rank1: supertrend_multi score=72.1) |
| price_cluster (bounce_pct=0.030) | Sharpe=0.53, trades=50 → 역효과 → 0.025 복원 |
| Bundle OOS BTC 4h | 2/5 PASS (cmf=2.508, supertrend_multi=3.674) ← 동일 |

## 다음 사이클 (305): A(품질) + C(데이터) + F(리서치)
- narrow_range trend_regime_max=1.4 효과 측정 (PAPER_SIM_STRATEGY_PARAMS 추가)
- price_cluster close_window=60 단독 실험
- Bundle OOS narrow_range 재측정 (ATR 필터 효과)
