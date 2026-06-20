# Current Cycle Briefing

_Cycle 334 | 2026-06-20 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): OFI v2 delta_window=5 실험 → 역효과 확인 후 복원

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS 변경:
  - `{"trend_span": 20, "delta_window": 5}` 실험 (기본 delta_window=10에서 단축)
  - 결과: avg=2.962 (4.345→-1.383 악화), std=3.570 (0.907→+2.663 악화) → **FAIL** (4/5 PASS)
  - 원인: fold0 OOS=7.75 극단값 (lucky fold) + fold2 OOS=-0.86 FAIL
  - 즉시 복원: `{"trend_span": 20}` (delta_window=10 기본값 유지)
- **delta_window 그리드 탐색 완료**: 5(FAIL), 7(FAIL), 10(PASS,best) → 추가 탐색 불필요

### D(ML) 코드 개선: walk_forward.py lucky_fold 경고 로직 추가

- `src/backtest/walk_forward.py` BundleOOSResult.validate():
  - fold OOS Sharpe > avg+1.5*std AND > 5.0 시 WARNING 로그
  - 목적: 단일 lucky fold가 std를 왜곡하는 패턴 (delta_window=5 fold0=7.75) 조기 탐지
  - PASS/FAIL 로직 무변경, 진단 전용

### E(실행): live_paper_trader.py 초기화 검증

- 임포트/초기화 정상: `LiveState()`, `load_pass_strategies()` → 22 strategies
- `BUNDLE_PASS_PRIORITY` 5개 전략 정상 로드
- CSV fallback 로직 검토: Bybit 실패 → data/historical 실거래소 우선 정렬 정상

### F(리서치): OFI v2 파라미터 탐색 완료 기록

- OFI v2 파라미터 탐색 이력:
  - trend_span: 15(FAIL) < 25(PASS) < 20(PASS,best) — 완료 (Cycle 333)
  - delta_window: 5(FAIL), 7(FAIL), 10(PASS,best) — 완료 (Cycle 334)
- **다음 탐색 후보**: buy_thresh=0.30 (현재 0.25/-0.25)

## 시뮬레이션 결과

- Paper Sim BTC 1h (8 windows, 20전략): **0/20 PASS** (14사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, +2.19%, 1/8)
  - rank2: positional_scaling (Sharpe=0.00, +1.97%, 1/8)
- Bundle OOS BTC 4h (5-fold): **5/5 PASS** (delta_window=10 복원!)
  - OFI v2: PASS (avg=4.345, std=0.907, rank1) ← 기준 복원

## 테스트 결과

- **8425 passed, 23 skipped** (회귀 없음)
