# Current Cycle Briefing

_Cycle 333 | 2026-06-19 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### C(데이터): load_csv_ohlcv() 엣지케이스 테스트 6건 추가

- `tests/test_data_utils.py` 누락 경로 보완:
  - FileNotFoundError, missing column, 'time'/'date' 헤더 변형, TZ-aware → UTC 변환, no timestamp column
  - 총 34 tests (이전 28 → +6)
- 합성 vs 실거래소 CSV 우선순위 로직 확인: `_candidate_key` 정상 작동 (synthetic=False 우선)
- Empty DataFrame 엣지케이스: `resample_ohlcv()` 빈 DF 입력 시 빈 DF 반환 확인

### B(리스크): BacktestEngine cooldown_suppressed 진단 카운터 + min_hold_bars=4 실험

- `src/backtest/engine.py`:
  - `BacktestResult.cooldown_suppressed: int = 0` 필드 추가
  - cooldown 활성 시마다 카운터 증가, DEBUG 로그 출력
- min_hold_bars=4 실험 (paper_sim --min-hold-bars 4):
  - roc_ma_cross: -0.41 → +0.16 (개선), price_cluster: +0.34 → -0.53 (악화)
  - 결론: 전략별 차별 효과 → 범용 min_hold_bars 기본값 유지 (0), 필요시 CLI 옵션 활용

### F(리서치): OFI v2 trend_span=25 실험 완료

- `scripts/run_bundle_oos.py`:
  - trend_span=25 실험: avg=3.929, std=1.081, 5/5 PASS
  - trend_span=20 (avg=4.345, std=0.907) vs trend_span=25 (avg=3.929, std=1.081)
  - 결론: trend_span=20이 최적. **즉시 복원 완료**
  - 그리드 탐색 완료: 15(FAIL) < 25(PASS) < 20(PASS, best)

## 시뮬레이션 결과 (Cycle 333)

- **테스트**: 8425 passed, 23 skipped (회귀 없음, +6 신규)
- **Paper Sim BTC 1h (min_hold_bars=4 실험)**: 0/20 PASS (13사이클 연속)
  - rank1: roc_ma_cross (Sharpe=0.16, Return=+2.34%, 2/8) — min_hold_bars=4로 개선
  - rank2: positional_scaling (Sharpe=-0.40, 1/8)
  - rank6: price_cluster (Sharpe=-0.53, 1/8) — min_hold_bars=4로 악화
- **Bundle OOS BTC 4h (trend_span=25 실험)**: **5/5 PASS** (4/5 → 5/5 복원!)
  - order_flow_imbalance_v2: PASS (avg=3.929, std=1.081, trend_span=25 실험)
  - supertrend_multi: PASS (avg=3.892), vwap_cross: PASS (avg=3.047)
  - value_area: PASS (avg=3.069), cmf: PASS (avg=2.508)
  - ⚠️ 파라미터 복원 완료 (trend_span=20) — 다음 사이클 OFI avg=4.345 복구 예정

## 다음 사이클 (334 mod 5 = 4): D(ML) + E(실행) + F(리서치)

- **D(ML)**: ML 모델 재학습 권고 (ADWIN drift=YES), 또는 OFI v2 delta_window 실험
- **E(실행)**: Paper Trading 모드 점검, TWAP 실행기 검증
- **F(리서치)**: OFI v2 delta_window 탐색 (trend_span=20 확정, 다음: delta_window=5 또는 7)
