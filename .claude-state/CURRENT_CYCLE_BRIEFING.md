# Current Cycle Briefing

_Cycle 334 | 2026-06-20 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): OFI v2 delta_window=5 실험 → FAIL → 복원

- `scripts/run_bundle_oos.py`:
  - `{"trend_span": 20, "delta_window": 5}` 실험 (기본값 10 → 5)
  - 결과: OFI avg OOS Sharpe 4.345 → 2.962, std 0.907 → 3.570 — **FAIL**
  - fold2 OOS=-0.86 (delta_window=10 시 +3.458), std 3.570 > 2.0 임계 초과
  - 원인: 5봉 단기 window → 노이즈에 민감, 불안정한 신호 생성
  - **즉시 복원**: `{"trend_span": 20}` (delta_window=10 기본값 유지)
  - delta_window 그리드 확정: 5(FAIL) < 10(PASS,best)

### E(실행): live_paper_trader.py CSV fallback 검증

- `scripts/live_paper_trader.py` 코드 검토 완료:
  - `fetch_latest_candles()`: Bybit 실패 → data/historical/ CSV 자동 로드
  - 실거래소 CSV 우선(synthetic=False 정렬), 4h 요청 시 1h→resample 지원
  - 초기화 정상: BTC 200 candles 로드, `enrich_indicators()` 실행 완료
  - PASS 전략 22개 정상 로드 (QUALITY_AUDIT.csv 기반)
  - 코드 변경 없음 — 기존 구현이 안정적

### F(리서치): OFI v2 파라미터 탐색 결론 정리

- trend_span 그리드 탐색 완료 (이전 사이클 포함):
  - 15(FAIL,std=2.771) < 25(PASS,avg=3.929,std=1.081) < 20(PASS,best=4.345,std=0.907)
- delta_window 그리드 탐색 완료 (이번 사이클):
  - 5(FAIL,avg=2.962,std=3.570) < 10(PASS,best=4.345,std=0.907)
- 최적 파라미터 확정: `{"trend_span": 20}` (delta_window=10 기본값)
- 다음 탐색 후보: `imbalance_threshold` 파라미터 (전략 소스 확인 필요)

## 시뮬레이션 결과 (Cycle 334)

- **테스트**: 8425 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (표준)**: **0/20 PASS** (14사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, 1/8) — 표준 기준
  - rank2: roc_ma_cross (Sharpe=-0.41, 2/8)
  - 주요 FAIL 원인: profit_factor 1.5 미달 (전략 전반)
- **Bundle OOS BTC 4h (delta_window=5 실험)**: **4/5 PASS**
  - order_flow_imbalance_v2: FAIL (avg=2.962, std=3.570) ← 실험 결과, 파라미터 복원됨
  - supertrend_multi: PASS (avg=3.892), value_area: PASS (avg=3.069)
  - vwap_cross: PASS (avg=3.047), cmf: PASS (avg=2.508)
  - ⚠️ 파라미터 복원 → 다음 실행 시 5/5 PASS 복구 예정

## 다음 사이클 (335 mod 5 = 0): A(품질) + C(데이터) + F(리서치)

- **A(품질)**: profit_factor FAIL 원인 분석 + price_cluster/positional_scaling 개선 탐색
- **C(데이터)**: SOL/ETH synthetic 데이터 품질 점검, BTC CSV 커버리지 확인
- **F(리서치)**: OFI imbalance_threshold 파라미터 존재 여부 확인 후 탐색 결정
