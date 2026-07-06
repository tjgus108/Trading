# Current Cycle Briefing

_Last updated: 2026-07-06 (Cycle 399 완료)_

## 현재 상태

- **완료된 사이클**: 399
- **다음 사이클**: 400 (400 mod 5 = 0 → A+C+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.24 (baseline, weak_rsi_buy_max=40 기본값) — 탐색 방향 검토 필요
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (캐시, SSL 차단으로 갱신 불가)
- **전체 테스트 수**: 8555개 (+11)

## Cycle 399 주요 결과

### D(ML): RegimeDetector 미커버 엣지케이스 6개 추가

- `tests/test_ml_regime_detector.py`: `TestRegimeDetectorEdgeCases` 클래스 (6 tests)
  - minimum_warmup_bars 정확한 값 검증
  - 정확히 warmup_bars 데이터 → 계산 경로 진입 확인
  - NaN 비율 >10% → 이전 레짐 유지 (fallback)
  - atr_ma=0 → CRISIS/RANGE 조건 불충족 → None 반환
  - adx=25.0 정확히 → TREND 아님 (>25 조건 불충족)
  - confirm_bars=1 → 단 1봉으로 즉시 전환

### E(실행): PaperTrader 미커버 엣지케이스 5개 추가

- `tests/test_paper_trader.py`: 5개 테스트 추가
  - quantity=0 → rejected
  - price<0 → rejected
  - check_sl_tp() 포지션 없음 → hit=False
  - check_sl_tp() SL 체결 → hit=True, type='sl'
  - check_sl_tp() TP 체결 → hit=True, type='tp', pnl>0

### F(리서치): frama weak_rsi_buy_max=50 DEAD PARAM 확정

- **실험 결과** (paper_sim, weak_rsi_buy_max=50 vs 기본값40):
  - Sh: 0.24 → 0.44 (↑+0.20)
  - Trades: 40 → 65 (↑+25, RSI 40-50 구간 해제 효과 확인)
  - Consistency: 1/8 → **0/8** (↓악화 — DEAD PARAM 판정 근거)
  - PF: 1.12 → 1.11 (변화 없음)
- **판단**: Trades 증가는 신호 품질 저하로 인한 과다 거래 → DEAD
- **코드 변경**:
  - `scripts/paper_simulation.py`: 실험 파라미터 제거, 기본값 복원 + DEAD 결과 주석
  - `src/backtest/walk_forward.py`: weak_rsi_buy_max 그리드 주석화 (27→9 combos)

## 시뮬레이션 현황 (Cycle 399 생성)

| 전략 | Sharpe | PF | Trades | Consist | Pass |
|------|--------|-----|--------|---------|------|
| roc_ma_cross | 1.81 | 2.02 | 14 | 4/8 | **PASS** |
| price_cluster | 1.06 | 1.32 | 35 | 2/8 | FAIL |
| dema_cross | 0.85 | 1.38 | 26 | 2/8 | FAIL |
| frama | 0.24 | 1.12 | 40 | 1/8 | FAIL (wrbm=40 baseline 복원) |

Bundle OOS: **5/5 PASS** (캐시, 갱신 불가)
