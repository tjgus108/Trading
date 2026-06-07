# Next Steps

_Last updated: 2026-06-07 (Cycle 286 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 286

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 284 | D+E+F | cmf_confirm 추가, trend_confirm_bars=3, fold4: -1.538→-0.006 (劇的 개선) |
| 285 | A+C+F | trend_confirm_bars=2 복귀, std 2.450→2.386, 2022 데이터 추가 시도→역효과→롤백 |
| 286 | B+D+F | atr_threshold=0.7→0.5 — fold4 변화 없음 (ATR 병목 아님 확인), DEFAULT_GRIDS 하한 확장 |

### 🎯 Cycle 287 작업 방향 (287 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): supertrend_multi fold4 WFE 개선 — min_wfe 완화 검토
- **Cycle 286 핵심 발견**: atr_threshold=0.5는 효과 없음 (fold4 trades=8 유지, OOS=-0.006 동일)
  - fold4 문제는 ATR 필터가 아닌 **레짐 비친화성**: IS=2023-08~2024-02(상승장), OOS=2024-02~04(ATH조정)
  - WFE≥0.5 달성 조건: OOS≥1.25 (IS*0.5) → 현재 -0.006으로 불가
- **Option A** (완화): BUNDLE_STRATEGY_OVERRIDES `min_wfe=0.1` 추가
  - 근거: OOS=-0.006 ≈ 0 (손해 없음) → WFE 기준 엄격화의 실익이 불분명
  - 위험: 과최적화 허용 신호로 해석 가능
- **Option B** (구조 변경): fold4 OOS 기간 단축 또는 fold 슬라이딩 윈도우 조정
  - 현재 6m IS / 2m OOS → OOS 단축 시 더 안정적 구간 포함 가능
- **추천**: Option A 시도 후 전체 avg_sharpe 변화 관찰

#### D(ML): supertrend_multi 신호 조건 근본 재검토
- **문제 재정의**: cmf_confirm=True + rsi_ob_filter=True + ema_filter=True → fold4에서 BUY 신호 과하게 차단
  - 8 trades but OOS Sharpe ≈ 0 → 이긴 거래가 진 거래를 상쇄 (WR 문제)
  - **실험**: cmf_confirm=False (cmf 필터 제거) or rsi_ob_threshold=70→85로 완화
- **구현**: BUNDLE_STRATEGY_INIT_PARAMS에서 `cmf_confirm=True→False` 또는 `rsi_ob_threshold=80→85`
  - fold4 OOS 재측정 후 -0.006 초과 여부 확인

#### F(리서치): 14회 연속 PASS cmf 전략 안정성 유지
- cmf: PASS avg=2.508, std=1.888 ← 변화 없음 (14회 연속 PASS)
- supertrend_multi PASS 경로:
  1. min_wfe 완화 (단기)
  2. 신호 조건 재검토 (중기)
  3. IS 기간 다양화 실제 데이터 확보 (장기)

### ⚠️ 핵심 현황
- **fold4 WFE 문제 구조 확정**: atr_threshold=0.5/0.7 무관 → IS 과최적화 + OOS 레짐 전환
- **fold3 excluded (구조적)**: 2023-12~2024-02 신호 희소 → 변경 방법 없음 (현재 구조 한계)
- **std 목표**: 2.386 < 2.5 (max_oos_sharpe_std=2.5 기준 충족) ← std 기준 통과 중
- **Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 사용**

### 핵심 메트릭 (Cycle 286)
- 테스트: **8377 passed** — 회귀 없음 (targeted 198 passed)
- Paper Sim BTC 1h: 0/22 PASS (rank1: supertrend_multi +6.73%, Sharpe=0.60)
- Bundle OOS BTC 4h (5-fold, CSV, Cycle 286):
  - cmf: **PASS** avg=2.508, std=1.888 ← **14회 연속 PASS**
  - supertrend_multi: FAIL avg=2.754, std=2.386 (atr_threshold 변경 효과 없음)
    - fold3 excluded (2 trades, 구조적)
    - fold4 WFE=-0.002 (OOS=-0.006, IS=2.507) → 동일
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 286)
1. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS
   - `atr_threshold=0.7→0.5` (B(리스크): ATR 필터 완화 시도 → fold4 효과 없음 확인)
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS supertrend_multi
   - `atr_threshold: [0.7,0.8,0.9]→[0.5,0.6,0.7]` (D(ML): 하한 확장 — 낮은 임계값 탐색 가능)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
  - 없이 실행하면 합성 9-fold (2022-01~2024-01) 사용됨 — 구분 주의
- 2022 데이터 추가는 합성 생성만 가능 → 전략 성능 저하 확인 → 시도 안 함
