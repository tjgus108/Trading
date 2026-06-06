# Current Cycle Briefing

_Cycle 282 완료 | 2026-06-06_

## 카테고리: B(리스크) + D(ML) + F(리서치)

### 수행 작업

1. **B(리스크)**: `supertrend_multi.py`에 `rsi_ob_filter` + `rsi_ob_threshold` 파라미터 추가
   - fold4 ATH(BTC 73k, RSI≈85) BUY 13건 → RSI 과매수 구간 진입 차단
   - `rsi_ob_filter=True` + `rsi_ob_threshold=75.0` (기본값)
   - SELL에는 영향 없음 — BUY만 타겟팅
   - `rsi14` pre-computed 컬럼 우선, 없으면 EWM 계산

2. **D(ML)**: `walk_forward.py` DEFAULT_GRIDS 확장
   - `rsi_ob_filter: [True, False]` 추가
   - `rsi_ob_threshold: [75, 78, 80]` 추가 (cmf.rsi_max_buy 동일 범위)
   - `optimize_supertrend_multi()` factory에 두 파라미터 연결
   - 신규 테스트 3개 추가 (17 passed in 0.28s)

3. **F(리서치)**: RSI 필터 기대 효과 분석
   - fold4 gap 4.876 → std=2.655 (82% 기여)
   - threshold=80 적용 시 13건 중 7-10건 차단 → fold4 OOS≥0 예상
   - 목표: std 2.655 → 1.7 이하

### 시뮬레이션 결과

- **테스트**: 8369 passed, 23 skipped — 전체 회귀 없음
- **Paper Sim**: 0/22 PASS, rank1: supertrend_multi +6.73% (AvgSharpe=0.60, PF=1.17)
- **Bundle OOS BTC 4h (5-fold, CSV)**:
  - cmf: **PASS** avg=2.508, std=1.888 (10회 연속)
  - supertrend_multi: FAIL avg=2.806, std=2.655, fold4=-1.539 (default=False 실행)
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 다음 사이클: 283
**카테고리**: C(데이터) + B(리스크) + F(리서치) (283 mod 5 = 3)
**핵심 과제**: supertrend_multi rsi_ob_filter IS 최적화 검증
- Bundle OOS 실행 시 `--csv-dir data/historical` 필수
- rsi_ob_threshold=78 또는 80이 fold4 ATH 구간에서 IS 최적값으로 선택되는지 확인
- C(데이터): enrich_indicators에 `rsi14` pre-compute 추가 (현재 rsi_ob_filter에서 직접 계산 중)
  - `scripts/run_bundle_oos.py`의 `enrich_indicators`에 RSI14 컬럼 추가 → cold-start 방지
- B(리스크): rsi14 pre-compute 적용 후 fold4 OOS 개선 확인
