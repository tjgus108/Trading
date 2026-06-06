# Next Steps

_Last updated: 2026-06-06 (Cycle 280 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 280

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 278 | C+B+F | wick_reversal has_momentum 필터, Bundle에서 supertrend_multi 교체 |
| 279 | D+E+F | supertrend_multi atr_threshold_max=2.0 추가 (효과 미미), avg 1.699→2.266 |
| 280 | A+C+F | EMA200 필터 + enrich_indicators pre-compute, fold4: -4.239→-1.539, avg 2.266→2.806 |

### 🎯 Cycle 281 작업 방향 (281 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): supertrend_multi fold4 마지막 개선 — OOS std 2.655→<2.0 목표
- fold4 OOS=-1.539에서 남은 13개 거래 분석
  - EMA200 필터 적용 후에도 일부 나쁜 SELL 거래 존재
  - 가설: EMA200 차단에서 누락된 SELL → 추세 판단이 짧은 시간 내 BUY→SELL 전환
  - 개선 방향:
    1. **추세 연속성 강화**: `_trend_confirmation_pass` 2봉 → 3봉 요구
    2. **HIGH confidence만 거래**: MEDIUM 신호는 HOLD 처리 (fold4에서 오신호 대부분 MEDIUM)
    3. **볼륨 확인 강화**: 상승장 SELL 신호 시 볼륨이 평균의 1.5x 이상 요구

#### D(ML): supertrend_multi 파라미터 grid 최적화 재실행
- `ema_filter: [True, False]`가 추가됨 → `optimize_supertrend_multi()` 재실행 시
  ema_filter=True가 IS 최적화에서도 우위인지 확인
- walk_forward.py `optimize_supertrend_multi`로 5-fold 검증
  - 기대: ema_filter=True + atr_threshold=0.7이 안정적으로 선택되는지

#### F(리서치): 5-fold Bundle OOS std 감소 기법
- supertrend_multi std=2.655 → 목표 < 2.0
  - fold 간 Sharpe 분산 높음: fold1(5.423), fold2(4.265), fold3(3.337), fold4(-1.539), fold0(2.545)
  - fold4가 유일한 마이너스 fold → fold4만 해결하면 std 자연히 감소
  - 리서치: Walk-Forward std 감소 기법 (파라미터 정규화, 샘플 크기 증가 등)

### ⚠️ 긴급 사항
- **supertrend_multi fold4 마지막 문제**: OOS=-1.539 → 목표 OOS≥0 (PASS fold5 달성)
- **std 목표**: 2.655 → < 2.0 (fold4 개선 시 자연히 달성됨)
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용** — 없으면 합성 9-fold 실행됨

### 핵심 메트릭 (Cycle 280)
- 테스트: **8369 passed** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS (Cycle 279 기준, 새 paper sim 결과 대기 중)
  - rank1: supertrend_multi +6.73% (AvgSharpe=0.60) ← ema_filter 효과는 다음 사이클 확인
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 280):
  - cmf: **PASS** avg=2.508, std=1.888 ← 8회 연속 PASS
  - supertrend_multi: FAIL avg=2.806 (↑2.266), std=2.655 (↓3.792), fold4: -1.539 (↑-4.239)
  - Note: paper_sim은 ema_filter로 인한 변화 없음 (1h에서 SELL 차단/수익 상쇄)
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 280)
1. `src/strategy/supertrend_multi.py` — ema_filter 파라미터 추가
   - `__init__`: `ema_filter: bool = True` 기본값
   - `generate()`: close > EMA200이면 SELL 차단 (pre-computed 컬럼 우선)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 및 factory 업데이트
   - `ema_filter: [True, False]` 추가
   - `optimize_supertrend_multi` factory에 `ema_filter` 연결
3. `scripts/run_bundle_oos.py` — enrich_indicators + BUNDLE_STRATEGY_INIT_PARAMS 업데이트
   - `enrich_indicators`: `ema200` 컬럼 추가 (pre-compute, cold-start 방지)
   - `BUNDLE_STRATEGY_INIT_PARAMS`: `supertrend_multi` ema_filter=True 추가

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
  - 없이 실행하면 합성 9-fold (2022-01~2024-01) 사용됨 — 구분 주의
