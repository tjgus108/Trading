# Current Cycle Briefing

_Cycle 332 | 2026-06-19 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): paper_simulation.py --min-hold-bars CLI 인자 추가

- `scripts/paper_simulation.py`:
  - `--min-hold-bars INT` argparse 인자 추가 (기본 0=비활성)
  - `run_simulation(min_hold_bars: int = 0)` 파라미터 추가
  - `BacktestEngine(min_hold_bars=min_hold_bars)` 전달
  - args.min_hold_bars > 0 시 "[CONFIG] min_hold_bars overridden: N" 출력
- 검증: `python3 scripts/paper_simulation.py --help` 에서 `--min-hold-bars` 노출 확인

### D(ML): order_flow_imbalance_v2 그리드 탐색 — trend_span=15, delta_window=7 실험

- `scripts/run_bundle_oos.py` + `scripts/paper_simulation.py`:
  - `{"trend_span": 20}` → `{"trend_span": 15, "delta_window": 7}` 실험
  - Bundle OOS 결과: avg=4.036 (4.345→-0.309 악화), std=2.771 (0.907→+1.864 악화) → FAIL
  - Paper Sim: OFI rank11 (avg_sharpe=-1.03)
  - 원인: fold0 OOS=6.724 극단값 + fold4 OOS=1.189 → std 폭발
  - **즉시 복원**: `{"trend_span": 20}` (원상복구)
  - **결론**: trend_span=15 단기 추세 필터 → 노이즈 증가, 신호 불안정화

### F(리서치): 1h 12연속 FAIL 정책 확정

- Paper Sim BTC 1h 12사이클 연속 0/20 PASS
- 1h 전략 파라미터 실험 무기한 중단 결정
- 4h OFI 탐색 계속: trend_span=25 다음 차례 (15 역효과 확인)

## 시뮬레이션 결과 (OFI 실험 파라미터 적용)

- **테스트**: 8419 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h**: 0/20 PASS (12사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, 1/8)
- **Bundle OOS BTC 4h (실험 중)**: 4/5 PASS (OFI 파라미터 실험 FAIL)
  - order_flow_imbalance_v2: FAIL (avg=4.036, std=2.771) ← trend_span=15 실험
  - supertrend_multi: PASS (avg=3.892, std=1.239)
  - value_area: PASS (avg=3.069)
  - vwap_cross: PASS (avg=3.047)
  - cmf: PASS (avg=2.508)
  - ⚠️ OFI 파라미터 복원 완료 (trend_span=20) → 다음 사이클 5/5 복구 예정

## 다음 사이클 (333 mod 5 = 3): C(데이터) + B(리스크) + F(리서치)

- **C(데이터)**: src/data/ 모듈 엣지케이스 테스트 점검 (CSV 로딩 안정성)
- **B(리스크)**: --min-hold-bars 4 실제 효과 측정 (price_cluster Sharpe 변화)
- **F(리서치)**: OFI v2 trend_span=25 실험 (목표: avg>5.0, std<0.8)
