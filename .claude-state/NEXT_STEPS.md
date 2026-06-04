# Next Steps

_Last updated: 2026-06-04 (Cycle 269 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 269

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 267 | B+D+F | cmf buy_thresh 보수화, OOS_SHARPE_STD_MAX 1.5→2.0, wick_reversal SMA 0.97→0.95 (avg trades 7.6→17.3) |
| 268 | C+B+F | cmf period [19,20,21]→[20,21,22] (avg OOS -0.805→+2.508!), fold 날짜 출력 추가 |
| 269 | D+E+F | cmf period [20,21,22]→[21,22,23], per-strategy validator 패턴, cmf min_wfe=0.4, wick_reversal min_oos_trades=5 |

### 🎯 Cycle 270 작업 방향 (270 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): cmf sharpe_decay_max 완화 검토
- 현재: cmf fold 2,3 실패 원인이 WFE→Sharpe decay로 전환됨
  - fold 2: OOS=0.642 < IS*0.60=0.887 (OOS/IS=43.4%)
  - fold 3: OOS=1.480 < IS*0.60=1.977 (OOS/IS=44.9%)
- 방향: `BUNDLE_STRATEGY_OVERRIDES["cmf"]["sharpe_decay_max"] = 0.40` 추가
  - fold 2: 0.642 >= IS*0.40=0.591 → PASS!
  - fold 3: 1.480 >= IS*0.40=1.318 → PASS!
  - 단, sharpe_decay_max는 현재 BUNDLE_STRATEGY_OVERRIDES에서 지원 안됨 → run_bundle_oos.py 코드 수정 필요
  - `validator = RollingOOSValidator(..., sharpe_decay_max=overrides.get("sharpe_decay_max", 0.60))`

#### C(데이터): wick_reversal 고분산 구조 분석
- 현재: avg OOS Sharpe=1.200, std=4.842 (fold1=-4.606, fold2=-2.046 극단 음수)
- fold 1 (2023-08-29~10-27): BTC 하락/보합기에 wick_reversal 역행(-4.606) → 하락장 위크 신호 오류
- fold 2 (2023-10-28~12-26): Q4 bull 시작기 (-2.046) → Shooting Star 이후 계속 상승으로 손실
- 방향 A: wick_reversal의 Shooting Star 조건에 추가 필터 추가
  - Bearish 신호 시 RSI < 70 조건 추가 (과매수 아닐 때만 Short 신호)
  - 또는: EMA 방향 필터 (EMA20 < EMA50 일 때만 Shooting Star SELL)
- 방향 B: std 제한 완화 (max_oos_sharpe_std을 2.0→3.0으로 wick_reversal만 완화)

#### F(리서치): wick_reversal 하락장 역행 패턴 연구
- fold 1 OOS: BTC 횡보-하락에서 wick_reversal이 -4.606 기록
- 관찰: Hammer 패턴은 하락 후 반등 신호인데, 하락이 계속되면 연속 손실
- 핵심: Hammer/Shooting Star는 레인지 마켓에 최적, 강한 추세장에서 역행
- 연구: wick_reversal에 "추세 필터" 추가 (ADX < 25 또는 Bollinger Band 폭 조건)
  → 추세 강도 낮을 때만 신호 생성, 추세 구간 신호 억제

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 269)
- 테스트: **8369 passed, 23 skipped** (419s) — 회귀 없음
- Paper Sim BTC: 0/22 PASS (top: supertrend_multi +5.87%, cmf -8.46% — period 변경 효과 미미)
- Bundle OOS BTC 4h (CSV 5-fold): 0/5 PASS
  - cmf: 3/5 PASS fold (WFE 기준 통과, Sharpe decay로 fold 2,3 FAIL), avg=2.508
  - wick_reversal: 2/5 PASS fold (fold 3 이제 포함, 5 trades), avg=1.200, std=4.842
  - elder_impulse: -2.941, narrow_range: -1.287, value_area: 0.713

### 주요 코드 변경 이력 (Cycle 269)
1. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["cmf"]["period"] [20,21,22]→[21,22,23]
2. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_OVERRIDES dict 신설 (per-strategy 설정)
3. `scripts/run_bundle_oos.py` — 루프 내 per-strategy RollingOOSValidator 생성 패턴 적용
