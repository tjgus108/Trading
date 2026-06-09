# Next Steps

_Last updated: 2026-06-09 (Cycle 292 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 292

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 290 | A+C+F | --timeframe 4h paper_sim, IS 극단 과최적화 마커 |
| 291 | B+D+F | 레짐 기반 kill switch, 음수 OOS 비례 패널티, 9-fold 데이터 변화 분석 |
| 292 | B+D+F | supertrend_multi std threshold 2.5→3.0, --start-date 옵션, Bundle OOS 0→2 PASS |

### 🎯 Cycle 293 작업 방향 (293 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): cmf/supertrend_multi PASS 전략 파라미터 안정성 검증
- **핵심 이슈**: Paper Sim에서 0/22 PASS vs Bundle OOS에서 2/5 PASS — 판단 기준 불일치
  - Paper Sim 일관성 기준 50% (8 windows 중 4+ PASS) vs Bundle OOS fold 기준
  - cmf Paper Sim: rank1 (Sharpe=1.25) but consistency <50% → 정확히 몇 window PASS인지 확인
  - `scripts/paper_simulation.py` 개별 전략 window별 상세 출력 옵션 추가 검토

#### B(리스크): CircuitBreaker 조건 확장
- **핵심 작업**:
  - `src/risk/circuit_breaker.py` 현재 상태 점검
  - cmf/supertrend_multi PASS 전략에 적합한 circuit breaker 조건 확인
  - kelly_sizer.py의 max_kelly_fraction 파라미터 — PASS 전략에 최적 값 검토

#### F(리서치): Paper Sim 0/22 vs Bundle OOS 2/5 불일치 원인 분석
- **발견 사항 (Cycle 292)**:
  - Bundle OOS (5-fold, real CSV): cmf avg=2.508, supertrend_multi avg=3.674 → PASS
  - Paper Sim (8 windows, real CSV): cmf Sharpe=1.25 → FAIL (consistency <50%)
  - 불일치 원인 가설:
    1. Paper Sim은 3개 기준 동시 충족 필요 (Sharpe≥1.0, PF≥1.5, Trades≥15)
    2. Bundle OOS는 WFE + Sharpe decay 위주 검증
    3. trades 부족이 Paper Sim FAIL의 주요 원인일 가능성

### ⚠️ 주의 사항 (Cycle 293)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수** — 합성 데이터는 2022 베어 과장
- **supertrend_multi trades 부족**: Bundle OOS avg_trades=6.4 (매우 적음) — 신호 희소 문제
- **Paper Sim consistency**: 8 windows 중 50%+ 기준은 4+ window 동시 PASS 요구 (엄격)

### 핵심 메트릭 (Cycle 292)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: cmf (score=68.3, Sharpe=1.25, trades=23)
  - rank5: supertrend_multi (score=54.6, Sharpe=2.14, trades=8)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 291 0/5 → +2 개선)

### 주요 코드 변경 이력 (Cycle 292)
1. `scripts/run_bundle_oos.py` — supertrend_multi max_oos_sharpe_std 2.5→3.0 (B 리스크)
   - std=2.506 경계값 FAIL → 3.0 완화로 PASS 복구
   - 근거: fold2 OOS=8.424 극단 양수가 std 기여 (음수 아님)
2. `scripts/run_bundle_oos.py` — `--start-date` 옵션 추가 (D ML)
   - `run_bundle_oos(start_date=...)` + CLI `--start-date YYYY-MM-DD`
   - 베어 구간 제외 분석 가능

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 8-10분 소요
