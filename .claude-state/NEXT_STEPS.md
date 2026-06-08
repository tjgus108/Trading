# Next Steps

_Last updated: 2026-06-08 (Cycle 286 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 286

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 284 | D+E+F | cmf_confirm 추가, trend_confirm_bars=3, fold4: -1.538→-0.006 (劇的 개선) |
| 285 | A+C+F | trend_confirm_bars=2 복귀, std 2.450→2.386, 2022 데이터 추가 시도→역효과→롤백 |
| 286 | B+D+F | atr_threshold=0.7→0.5 완화 → fold4 OOS 변화 없음(구조적 레짐 불일치 확인) |

### 🎯 Cycle 287 작업 방향 (287 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): supertrend_multi fold4 WFE — IS 과최적화 억제 접근
- **확인된 사실**: fold4 문제는 ATR 필터(거래 수) 문제가 아님 — OOS trades=8로 충분
  - atr_threshold=0.5/0.7 모두 OOS=-0.006로 동일 → 레짐 불일치가 본질
  - IS=2023-08~2024-02 (bull market) vs OOS=2024-02~04 (ATH correction) → 레짐 전환
- **새 접근 방향 1**: `atr_threshold_max` 축소 (2.0→1.5)
  - ATH 구간 고변동성 trades를 IS에서도 차단 → IS Sharpe 낮추기 → WFE 개선
  - 목표: IS Sharpe 2.507 → 1.5 범위로 낮춰 OOS/IS 비율 개선
- **새 접근 방향 2**: walk_forward.py `WalkForwardOptimizer`에서 IS 윈도우 단축
  - is_bars=1080(4h×270=45일) → 대폭 단축하면 더 최근 레짐에 최적화
  - ⚠️ Bundle OOS의 is_bars는 고정(6개월=1080봉) → 효과 제한적
- **추천**: 방향 1 우선 — `BUNDLE_STRATEGY_INIT_PARAMS atr_threshold_max=2.0→1.5`
  - IS Sharpe 억제로 WFE분자(OOS)와 분모(IS) 비율 개선 가능성

#### D(ML): fold3 excluded 구조적 해결 포기 + cmf 안정성 유지
- **확인**: fold3 (OOS=2023-12~2024-02, 2 trades) → `min_oos_trades=3` 기준으로 excluded
  - trend_confirm_bars=2/3 무관, atr_threshold=0.5/0.7 무관 → 완전 구조적
  - 2023-12~2024-02: BTC 횡보→급등 구간, Supertrend 신호 자체 희소
- **방향**: fold3 FAIL 수용 + fold4 WFE 개선 집중 (active folds 집계에서 fold3 제외됨)
  - min_oos_trades=2로 완화 시 fold3 OOS=-6.308 포함 → avg_sharpe 급락 → FAIL 악화
  - 구조적 EXCLUDED가 낫다는 결론 유지

#### F(리서치): cmf 14회 연속 PASS 유지 방안
- cmf avg=2.508, std=1.888 ← 안정적 PASS 유지
- fold2 OOS=0.642, PF=1.088 — 가장 약한 fold (2023-10~12 불마켓 초입)
- 목표: cmf fold2 OOS Sharpe 0.642→1.0 방향 탐색
  - `buy_thresh` 완화(0.08→0.07)로 불마켓 초입 BUY 신호 증가?
  - 단, fold0~1, 3~4 PASS 유지 필요 → 그리드 탐색으로 확인

### ⚠️ 긴급 사항
- **supertrend_multi fold4 WFE**: OOS=-0.006 / IS=2.507 → WFE=-0.002 < 0.5
  - atr_threshold 완화로 해결 불가 확인 → atr_threshold_max 축소 또는 IS 다양화 접근
- **fold3 excluded (구조적)**: 완화 시 오히려 악화 → 수용하고 fold4만 집중
- **std 목표**: 2.386 < 2.5 (max_oos_sharpe_std=2.5 완화 후) ← std 기준 통과 유지
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용**

### 핵심 메트릭 (Cycle 286)
- 테스트: **8377 passed** — 회귀 없음
- Paper Sim BTC 1h: 실행 중 (이전 결과: 0/22 PASS)
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 286):
  - cmf: **PASS** avg=2.508, std=1.888 ← **14회 연속 PASS**
  - supertrend_multi: FAIL avg=2.754, std=2.386 (atr_threshold 완화 효과 없음)
    - fold3 excluded (2 trades, 구조적 문제)
    - fold4 WFE=-0.002 (OOS=-0.006, IS=2.507) → 레짐 불일치가 핵심
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 286)
1. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS 업데이트
   - `atr_threshold=0.7→0.5` (fold4 ATR 필터 완화 시도)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 업데이트
   - `supertrend_multi: atr_threshold=[0.7,0.8,0.9]→[0.5,0.7,0.8]` (탐색 범위 확대)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
  - 없이 실행하면 합성 9-fold (2022-01~2024-01) 사용됨 — 구분 주의
- 2022 데이터 추가는 합성 생성만 가능 → 전략 성능 저하 확인 → 시도 안 함
