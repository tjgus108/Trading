# Current Cycle Briefing

_Cycle 305 완료 — 2026-06-13_

## 완료된 작업

### A(품질) — narrow_range walk_forward 그리드 확장
- `src/backtest/walk_forward.py`: narrow_range DEFAULT_GRIDS에 2개 파라미터 추가
  - `trend_regime_filter: [False, True]` — Cycle304 E에서 구현된 기능 WF 탐색에 포함
  - `atr_trend_max: [1.3, 1.4, 1.5]` — ATR 임계값 민감도 탐색
  - 총 유효 조합: 12개 (grid explosion 없음)
- 목적: fold3 OOS=-10.794 (2024-01~02 BTC 급등) 극단 손실 억제

### C(데이터) — price_cluster close_window=60 단독 실험
- `scripts/paper_simulation.py`: close_window=50→60 변경
  - Paper Sim BTC: rank1 score=75.7 (+1.9 vs Cycle304 73.8)
  - SharpeStd=1.77 (안정성 향상)
  - **결론**: close_window=60 소폭 개선 → 유지 확정 (reverting 불필요)

### F(리서치) — cmf/supertrend_multi 타임프레임 의존성 분석
- cmf: 4h에서만 강세 (5/5 PASS), 1h에서는 rank15 (노이즈 취약)
- supertrend_multi: 4h OOS PASS(Sharpe=3.674), 1h에서도 rank2 — 다중 타임프레임 유효
- narrow_range: fold3 극단 손실 원인 확인 → trend_regime_filter 그리드 추가로 대응

## 시뮬레이션 결과
- 테스트: **8394 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h: 0/22 PASS, price_cluster rank1 (score=75.7, +1.9 개선)
- Bundle OOS: **2/5 PASS** (cmf, supertrend_multi) — 이전 사이클 동일

## 다음 Cycle 306 (306 mod 5 = 1 → B+D+F)
- B(리스크): close_window=60 효과를 Bundle OOS 4h에서 검증
- D(ML): narrow_range trend_regime_filter + atr_trend_max walk-forward 실험
- F: cmf 1h 성능 저하 원인 심층 분석 (period 보수화 검토)
