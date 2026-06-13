# Current Cycle Briefing

_Cycle 304 완료 — 2026-06-13_

## 완료된 작업

### D(ML) — bounce_pct=0.030 실험 + walk_forward 그리드 업데이트
- `scripts/paper_simulation.py`: bounce_pct=0.030 실험 → 역효과 확인 → 0.025 복원
  - 결과: Sharpe 3.76(동일), PF 2.28→**2.07** (-9%), trades 12→13 (미미)
  - **결론**: bounce_pct=0.025가 최적. threshold 완화는 신호 품질 저하 (PF -9%)
- `src/backtest/walk_forward.py`: price_cluster close_window [40,50]→[50,60]
  - Cycle303에서 40 역효과 실증 → 40 제거, 60 추가 탐색

### E(실행) — NarrowRange trend_regime_filter 추가
- `src/strategy/narrow_range.py`: 새 파라미터 추가
  - `trend_regime_filter=False` (기본 비활성)
  - `atr_trend_max=1.4` (ATR/ATR_MA 임계값)
  - Bundle OOS 분석: fold1(-3.828)/fold3(-10.794) 고변동성 bull 구간에서 극단적 FAIL
  - 해결책: ATR/ATR_MA > 1.4 시 신호 억제 → 고변동성 추세장 오신호 방지

### F(리서치) — Bundle OOS PASS 전략 분석
- cmf: 5/5 PASS (Sharpe=2.508, PF=1.387) — 가장 일관된 성과
- supertrend_multi: PASS (OOS Sharpe=3.674, PF=2.475) — 높은 기대수익, fold3/4 거래 부족
- narrow_range: FAIL — 고변동성 bull 구간 취약성 확인, trend_regime_filter로 개선 시도

## 시뮬레이션 결과
- Paper Sim BTC 4h: 0/22 PASS, price_cluster rank1 (score=73.8, Sharpe=3.76, PF=2.07→0.025 복원 후 2.28)
- Bundle OOS: **2/5 PASS** (cmf, supertrend_multi) — 이전 사이클 동일

## 다음 Cycle 305 (305 mod 5 = 0 → A+C+F)
- A(품질): NarrowRange trend_regime_filter 그리드 추가 → walk_forward 실험
- C(데이터): price_cluster close_window=60 단독 실험 (50 유지하면서 60 비교)
- F(리서치): cmf/supertrend_multi 안정성 분석
