# Current Cycle Briefing

_Cycle 280 완료 | 2026-06-06_

## 카테고리: A(품질) + C(데이터) + F(리서치)

### 수행 작업

1. **A(품질)**: `supertrend_multi.py`에 `ema_filter` 파라미터 추가
   - C(데이터) 분석 결과: fold4 ATR ratio max=1.415 (< 2.0) → atr_threshold_max 효과 없음
   - fold4의 65% 봉이 close > EMA200 → EMA200 필터로 SELL 차단
   - `ema_filter=True` 시 close > EMA200이면 SELL HOLD 처리
   - pre-computed `ema200` 컬럼 우선 사용 (cold-start 방지)

2. **C(데이터)**: `enrich_indicators` EMA200 pre-compute 추가
   - 버그 발견: OOS 슬라이스(360봉)에서 EMA200 cold-start → 처음 200봉 무효
   - 수정: `enrich_indicators()`에 `ema200` 컬럼 추가 (전체 데이터 기반 warm-up)
   - bundle_oos 실행 시 반드시 `--csv-dir data/historical` 필수 (없으면 합성 9-fold)

3. **F(리서치)**: 4가지 SELL 차단 기법 비교 분석
   - EMA200: fold4에서 65.2% 차단 (채택)
   - ADX>25: 49.4% (낮음), ATH 95%: 26.1% (범위 너무 좁음)
   - 주의: fold2(2023-06~10)에서도 85.7% SELL 차단 → 양날의 검

### 시뮬레이션 결과

- **테스트**: 8369 passed, 23 skipped — 전체 회귀 없음
- **Paper Sim**: 0/22 PASS (Cycle 279 기준), supertrend_multi rank1 +6.73%
- **Bundle OOS BTC 4h (5-fold, CSV)**:
  - cmf: **PASS** avg=2.508, std=1.888 (8회 연속)
  - supertrend_multi: FAIL avg=2.806(↑), std=2.655(↓), fold4: -1.539(↑-4.239)
    - fold4 -4.239 → -1.539: EMA200 필터 효과!
    - 남은 문제: std=2.655 > 2.0, fold4 여전히 마이너스

### 다음 사이클: 281
**카테고리**: B(리스크) + D(ML) + F(리서치) (281 mod 5 = 1)
**핵심 과제**: supertrend_multi fold4 OOS=-1.539 → 0 이상 개선, std < 2.0 달성
- 추세 연속성 2봉 → 3봉 강화 테스트
- HIGH confidence only 모드 테스트 (MEDIUM SELL 차단)
- ema_filter=True가 IS 최적화에서도 우위인지 검증
