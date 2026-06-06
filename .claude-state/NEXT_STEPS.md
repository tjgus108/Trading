# Next Steps

_Last updated: 2026-06-06 (Cycle 282 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 282

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 280 | A+C+F | EMA200 필터 + enrich_indicators pre-compute, fold4: -4.239→-1.539 |
| 281 | B+D+F | confidence_filter 추가 (SELL-only), 핵심 발견: BUY가 문제 |
| 282 | B+D+F | rsi_ob_filter 추가, grid에 rsi_ob_threshold:[75,78,80] 연결 |

### 🎯 Cycle 283 작업 방향 (283 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): enrich_indicators에 RSI14 pre-compute 추가
- **현재 문제**: `rsi_ob_filter` 구현에서 매번 df에서 직접 RSI 계산 → cold-start 문제 발생 가능
  - OOS 슬라이스 360봉에서 RSI EWM alpha=1/14으로 계산 → 처음 50봉 동안 부정확
  - ema200처럼 전체 데이터에서 pre-compute 후 슬라이스에 보존 필요
- **수정 위치**: `scripts/run_bundle_oos.py` `enrich_indicators()` 함수
  - `delta = df['close'].diff(); gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); ...`
  - `df['rsi14'] = 100 - 100/(1+gain/loss)` 추가
- **효과**: `rsi14` 컬럼이 있으면 supertrend_multi.generate()에서 pre-computed 값 사용
  - fold4 ATH 구간 RSI 계산 정확도 향상 → 더 정밀한 차단

#### B(리스크): fold4 rsi_ob_filter 효과 검증
- Bundle OOS 재실행 시 rsi14 pre-compute 포함 여부 확인
- 예상: IS 최적화에서 rsi_ob_filter=True, threshold=78-80 선택
  - fold4 OOS=-1.539 → ≥0 (목표)
  - std 2.655 → <2.0 (목표)
- 만약 개선 없으면: `rsi_ob_threshold=[70, 72, 75]`로 범위 하향 검토

#### F(리서치): cmf 10회 연속 PASS 분석
- cmf avg=2.508, std=1.888 — 안정적 성과 유지 중
- cmf Paper Sim: AvgSharpe=-1.24, AvgReturn=-8.46% (1h 봉에서 부진)
  - 4h에서만 효과적? 타임프레임 특성 분석
  - 4h PASS, 1h FAIL 원인: 볼륨 노이즈, 신호 빈도 차이
- 데이터 충분 시 8h/daily 백테스트 검토

### ⚠️ 긴급 사항
- **supertrend_multi fold4 문제**: OOS=-1.539 → 목표 OOS≥0
  - rsi_ob_filter 추가됨 (Cycle 282), 다음 IS 최적화에서 효과 반영 예정
  - rsi14 pre-compute (C카테고리) → 계산 정확도 보장 후 재검증
- **std 목표**: 2.655 → < 2.0 (rsi_ob_filter 효과 검증 후 달성 가능)
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용**

### 핵심 메트릭 (Cycle 282)
- 테스트: **8369 passed** — 회귀 없음 (supertrend_multi 테스트 14→17개)
- Paper Sim BTC 1h: 0/22 PASS (rank1: supertrend_multi +6.73%, AvgSharpe=0.60, PF=1.17)
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 282):
  - cmf: **PASS** avg=2.508, std=1.888 ← 10회 연속 PASS
  - supertrend_multi: FAIL avg=2.806, std=2.655, fold4=-1.539 (default param)
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 282)
1. `src/strategy/supertrend_multi.py` — rsi_ob_filter + rsi_ob_threshold 파라미터 추가
   - `__init__`: `rsi_ob_filter: bool = False`, `rsi_ob_threshold: float = 75.0`
   - `generate()`: RSI 계산 후 RSI > threshold 시 BUY → HOLD (SELL은 무영향)
   - `rsi14` 컬럼 있으면 pre-computed 값 사용, 없으면 EWM 직접 계산
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 및 factory 업데이트
   - `rsi_ob_filter: [True, False]` 추가
   - `rsi_ob_threshold: [75, 78, 80]` 추가
   - `optimize_supertrend_multi` factory에 두 파라미터 연결
3. `tests/test_supertrend_multi.py` — 3개 신규 테스트 추가
   - test_rsi_ob_filter_blocks_buy_when_rsi_high
   - test_rsi_ob_filter_allows_buy_when_rsi_normal
   - test_rsi_ob_filter_does_not_block_sell

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
  - 없이 실행하면 합성 9-fold (2022-01~2024-01) 사용됨 — 구분 주의
