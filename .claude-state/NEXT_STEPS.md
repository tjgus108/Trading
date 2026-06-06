# Next Steps

_Last updated: 2026-06-06 (Cycle 281 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 281

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 279 | D+E+F | supertrend_multi atr_threshold_max=2.0 추가, avg 1.699→2.266 |
| 280 | A+C+F | EMA200 필터 + enrich_indicators pre-compute, fold4: -4.239→-1.539, avg 2.266→2.806 |
| 281 | B+D+F | confidence_filter 추가 (SELL-only), 핵심 발견: ema_filter가 이미 SELL 차단, fold4=BUY 신호 문제 |

### 🎯 Cycle 282 작업 방향 (282 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): supertrend_multi fold4 RSI 과매수 BUY 차단 실험
- **핵심 발견 (Cycle 281)**: fold4 (2024-02~04 ATH) bad trades = BUY 신호 (SELL이 아님)
  - ema_filter=True가 SELL 신호를 이미 차단
  - 남은 13개 BUY 거래가 ATH 피크에서 진입 → 단기 하락으로 OOS=-1.539
- **개선 방향: RSI 과매수 BUY 차단**
  - `rsi_ob_filter: bool = False` 파라미터 추가
  - when True: RSI14 > 75이면 BUY 신호 차단
  - 근거: cmf의 `rsi_max_buy: [75, 78, 80]`이 fold2,3 불마켓 구간에서 효과적이었음
  - 예상: fold4 ATH(BTC 73k, RSI>80) BUY 차단 → OOS 개선, std<2.0 달성 가능

#### D(ML): supertrend_multi RSI 필터 그리드 추가
- `rsi_ob_threshold: [75, 78, 80]` 추가 (cmf와 동일 범위)
  OR `rsi_ob_filter: [True, False]` 추가 (단순화)
- IS 최적화: rsi_ob_filter=True가 fold4 ATH에서 우위인지 확인
- walk_forward.py `optimize_supertrend_multi`에 연결

#### F(리서치): Walk-Forward OOS std 감소 분석
- supertrend_multi std=2.655 → 목표 < 2.0
  - fold4가 std의 82% 기여 (4.345 gap out of avg=2.806)
  - fold4 OOS=-1.539가 ≥0이 되면 std≈1.7 예상
  - RSI 필터로 fold4 bad BUY 13건 중 일부 제거 시 달성 가능

### ⚠️ 긴급 사항
- **supertrend_multi fold4 문제**: OOS=-1.539 → 목표 OOS≥0 (5fold 모두 PASS 달성)
  - BUY 신호 문제: RSI 과매수 필터가 핵심
  - confidence_filter는 이미 추가됨 (grid에 포함, ema_filter와 중복 없음)
- **std 목표**: 2.655 → < 2.0 (fold4 RSI 필터로 달성 가능)
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용** — 없으면 합성 9-fold 실행됨

### 핵심 메트릭 (Cycle 281)
- 테스트: **8369 passed** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS (rank1: supertrend_multi +6.73%, AvgSharpe=0.60)
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 281):
  - cmf: **PASS** avg=2.508, std=1.888 ← 9회 연속 PASS
  - supertrend_multi: FAIL avg=2.806 (=2.806), std=2.655 (=2.655), fold4: -1.539
  - Note: confidence_filter SELL-only는 ema_filter와 중복 → 추가 효과 없음
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 281)
1. `src/strategy/supertrend_multi.py` — confidence_filter 파라미터 추가
   - `__init__`: `confidence_filter: bool = False` 기본값
   - `generate()`: confidence_filter=True 시 SELL MEDIUM → HOLD (BUY는 항상 통과)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 및 factory 업데이트
   - `confidence_filter: [True, False]` 추가
   - `optimize_supertrend_multi` factory에 `confidence_filter` 연결
3. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS 유지 (confidence_filter default=False)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
  - 없이 실행하면 합성 9-fold (2022-01~2024-01) 사용됨 — 구분 주의
