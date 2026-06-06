# Current Cycle Briefing

_Cycle 281 완료 | 2026-06-06_

## 카테고리: B(리스크) + D(ML) + F(리서치)

### 수행 작업

1. **B(리스크)**: `supertrend_multi.py`에 `confidence_filter` 파라미터 추가
   - 실험: MEDIUM 신호 HOLD 처리 (both BUY+SELL) → fold0(-4.3), fold3(-3.0) 악화, avg 2.806→1.995
   - 수정: SELL-only confidence filter로 변경 → 결과 변화 없음
   - **핵심 발견**: ema_filter=True가 ATH SELL 신호를 이미 모두 차단
   - fold4 bad trades = BUY 신호 (ATH 피크에서 진입 후 단기 하락)
   - 다음 방향: RSI 과매수 BUY 차단 필요

2. **D(ML)**: `walk_forward.py` 최적화 그리드 확장
   - `confidence_filter: [True, False]` 추가 → IS 최적화에서 자동 탐색 가능
   - `optimize_supertrend_multi()` factory에 confidence_filter 연결

3. **F(리서치)**: Walk-Forward std 감소 메커니즘 분석
   - fold4(2024-02~04 ATH)가 std=2.655의 82% 기여
   - fold4 OOS=-1.539의 13건은 ALL BUY (ema_filter가 SELL 차단)
   - RSI 과매수(>75) BUY 차단 시 fold4 OOS≥0 달성 예상 → std≈1.7

### 시뮬레이션 결과

- **테스트**: 8369 passed, 23 skipped — 전체 회귀 없음
- **Paper Sim**: 0/22 PASS, rank1: supertrend_multi +6.73% (AvgSharpe=0.60)
- **Bundle OOS BTC 4h (5-fold, CSV)**:
  - cmf: **PASS** avg=2.508, std=1.888 (9회 연속)
  - supertrend_multi: FAIL avg=2.806 (=), std=2.655 (=), fold4: -1.539
    - 변화 없음 — confidence_filter(SELL-only)는 ema_filter와 중복
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 다음 사이클: 282
**카테고리**: B(리스크) + D(ML) + F(리서치) (282 mod 5 = 2)
**핵심 과제**: supertrend_multi fold4 RSI 과매수 BUY 차단으로 OOS≥0, std<2.0 달성
- `rsi_ob_filter: bool = False` 추가 → RSI14>75 시 BUY 차단
- grid: `rsi_ob_threshold: [75, 78, 80]` 또는 `rsi_ob_filter: [True, False]`
- cmf의 `rsi_max_buy` 패턴 참고 (fold2 불마켓 구간 효과적)
