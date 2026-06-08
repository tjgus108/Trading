# Next Steps

_Last updated: 2026-06-08 (Cycle 286 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 286

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 284 | D+E+F | cmf_confirm 추가, trend_confirm_bars=3, fold4: -1.538→-0.006 (劇的 개선) |
| 285 | A+C+F | trend_confirm_bars=2 복귀, std 2.450→2.386, 2022 데이터 추가 시도→역효과→롤백 |
| 286 | B+D+F | atr_threshold=0.5 무효 확인(cmf binding), cmf_period=10 역효과, DEFAULT_GRIDS 하향 조정 |

### 🎯 Cycle 287 작업 방향 (287 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): supertrend_multi fold4 — cmf 레짐 감지 방향 탐색
- **확인된 사실**: atr_threshold=0.5, cmf_period=10 모두 무효/역효과
  - atr_threshold: CMF가 binding → ATR 변경 무효
  - cmf_period=10: fold3 개선(+1.593)이지만 fold4 악화(-1.565), std=3.142 FAIL
- **핵심 문제**: fold4 IS(2023-08~2024-02 강세) vs OOS(2024-02~04 post-ATH) 레짐 전환
  - IS=2.507 과최적화, OOS=-0.006 (CMF<0 BUY 차단)
  - WFE < 0.5 구조적 FAIL → 레짐 전환 없이 해결 불가
- **다음 방안**: `min_wfe` 추가 완화 실험
  - 현재: `supertrend_multi` BUNDLE_STRATEGY_OVERRIDES에 `min_wfe` 없음 → default 0.5 사용
  - 시도: `min_wfe=0.2` 설정 → WFE=-0.002 여전히 FAIL이지만 기준 완화
  - 위험: WFE 기준 낮추면 과최적화 탐지 약화 → 신중 접근
- **대안**: fold4 WFE FAIL을 레짐 전환 마커로 처리하는 로직 추가
  - RollingOOSValidator에 `regime_transition_threshold` 파라미터 추가 (고려)

#### D(ML): cmf_period 중간값 탐색
- **실험 결론**: cmf_period=20(과소반응) vs cmf_period=10(과민반응) 모두 문제
  - cmf_period=20: fold3 OOS=-6.308 (2 trades excluded), fold4 OOS=-0.006
  - cmf_period=10: fold3 OOS=+1.593 (개선!), fold4 OOS=-1.565 (악화)
- **다음 시도**: cmf_period=15 탐색
  - fold3 개선 효과 부분 유지 + fold4 과민반응 완화 목표
  - 단, fold3는 2 trades excluded라 집계에서 제외 → 실효성 불확실
- **대안**: 현재 상태(cmf_period=20) 유지, D(ML) 작업 다른 방향 전환
  - walk_forward.py DEFAULT_GRIDS [0.5, 0.6, 0.7] — WalkForwardOptimizer 사용 전략에 영향

#### F(리서치): cmf 14회 연속 PASS 안정성 유지
- std=1.888 (목표 < 2.0) ← 안정적
- supertrend_multi PASS 경로: fold4 레짐 전환 문제 해결이 핵심
- **research focus**: WFE가 낮을 때 레짐 전환인지 과최적화인지 구분하는 방법론

### ⚠️ 긴급 사항
- **supertrend_multi fold4 WFE 구조적 FAIL**: 레짐 전환 문제 (bull→post-ATH)
  - atr_threshold, cmf_period 모두 시도 → 해결 불가
  - **min_wfe 완화 또는 레짐 감지 로직이 다음 경로**
- **fold3 excluded (구조적)**: 2023-12~2024-02 신호 희소, cmf_period=10 시 개선되나 fold4 악화
- **std 목표**: 2.386 < 2.5 (max_oos_sharpe_std=2.5) ← 기준 통과 중
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용**

### 핵심 메트릭 (Cycle 286)
- 테스트: **8377 passed** — 회귀 없음
- Paper Sim BTC 1h (8 windows): 0/22 PASS
  - rank1: supertrend_multi (score=73.9, sharpe=0.60, trades=48)
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 286):
  - cmf: **PASS** avg=2.508, std=1.888 ← **14회 연속 PASS**
  - supertrend_multi: FAIL avg=2.754, std=2.386 (변화 없음)
    - fold3 excluded (2 trades, 구조적)
    - fold4 WFE=-0.002 (OOS=-0.006, IS=2.507) ← 레짐 전환 구조적 FAIL
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 286)
1. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS 업데이트
   - `atr_threshold=0.7→0.5`: 효과 없음 확인 (cmf binding)
   - `atr_threshold_max=2.0→1.5`: IS 과최적화 방지
   - `cmf_period=10` 시도 후 복귀 (역효과 확인)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 업데이트
   - `atr_threshold`: [0.7, 0.8, 0.9] → [0.5, 0.6, 0.7]
   - `atr_threshold_max`: [1.5, 2.0, 3.0] → [1.5, 2.0, 2.5]

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
- 2022 데이터 추가는 합성 생성만 가능 → 전략 성능 저하 확인 → 시도 안 함
- Paper simulation: 22 전략 × 8 windows → 약 10분 소요 (Bash timeout 주의)
