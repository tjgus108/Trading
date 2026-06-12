# Current Cycle Briefing

_Cycle 302 완료 — 2026-06-12_

## 완료된 작업

### B(리스크): n_bins=7 실험 → 역효과, DrawdownMonitor 개선
- `scripts/paper_simulation.py`: n_bins=7 실험 → Sharpe 3.76→-1.76 역효과 → 복원
- `src/risk/drawdown_monitor.py`: tiered halt 회복 로직 개선
  - `_tiered_halt` + `_halt_drawdown` 상태 추가
  - 주간/일간 halt 후 tiered 조건 해소 시 더 빠른 재개 가능 (버그 수정)

### D(ML): atr_bounce_factor=1.5 실험 → 역효과, price_cluster 그리드 추가
- `scripts/paper_simulation.py`: atr_bounce_factor=1.5 (n_bins=7과 동시 실험) → 역효과 → 0.0 유지
  - ATR/close×1.5 ≈ 3~6% threshold (bounce_pct=2.5% 대비 2배+) → 오신호 증가
- `src/backtest/walk_forward.py`: price_cluster DEFAULT_GRIDS 추가
  - bounce_pct: [0.020, 0.025, 0.030], n_bins: [4,5,6], close_window: [40,50], vol_atr_trend_min: [1.3,1.5,2.0]

### F(리서치): microstructure bin 분석
- 7-10 지지/저항 레벨 이론 검증: BTC 4h에서 n_bins=7 역효과
- 원인: 좁은 bin + 넓은 ATR threshold = bin 경계 중첩 신호 → 노이즈
- **단독 실험 원칙 확립**: 두 파라미터 동시 변경 금지

## 시뮬레이션 요약

| 구분 | 결과 |
|------|------|
| Paper Sim PASS | 0/22 (실험 n_bins=7: price_cluster Sharpe -1.76, 복원 후 Cycle301과 동일) |
| Bundle OOS PASS | 2/5 (cmf, supertrend_multi) ← 동일 유지 |
| 테스트 스위트 | 8392 passed, 23 skipped |

## 다음 사이클 (303): C(데이터) + B(리스크) + F(리서치)
- C: close_window 50→40 **단독** 실험 (n_bins=5 유지, trades 증가 목적)
- B: DrawdownMonitor tiered halt 테스트 추가 (test_tiered_halt_recovery_faster_than_legacy)
- F: n_bins 독립 실험 근거 강화 (n_bins=6 단독 시도)
