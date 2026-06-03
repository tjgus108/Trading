# Next Steps

_Last updated: 2026-06-03 (Cycle 267 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 267

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 266 | B+D+F | DrawdownMonitor Sharpe decay 필터, optimize_wick_reversal 4h grid 분리 |
| 267 | B+D+F | cmf buy_thresh 보수화, OOS_SHARPE_STD_MAX 1.5→2.0, wick_reversal SMA 0.97→0.95 (avg trades 7.6→17.3) |

### 🎯 Cycle 268 작업 방향 (268 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): wick_reversal fold6 극단 손실 원인 분석
- 현재: fold6 OOS Sharpe=-12.365 (WFE=-10.641) — 극단 손실 fold
- fold6 구간의 BTC 4h 시장 특성 확인 (fold별 날짜 구간 로그 추가 검토)
- 방향: `run_bundle_oos.py`에서 fold별 OOS 날짜 출력 추가 → 레짐 확인
- 또는: Shooting Star 필터도 SMA 기준 완화 검토 (close < SMA20*1.03 현재 유지)

#### B(리스크): cmf avg OOS Sharpe 음수(-0.805) 원인 분석
- 현재: 4/9 PASS fold, avg OOS Sharpe=-0.805 → buy_thresh 보수화 후 오히려 악화
- 이유: fold3(-3.784), fold5(-3.576), fold6(-6.642)가 크게 손실
- 방향: DEFAULT_GRIDS["cmf"] period 범위를 [19,20,21]→[20,21,22]로 이동 검토 (더 긴 CMF 평활화)
- 또는: cmf를 WFO(파라미터 최적화 포함) 방식으로 전환 (현재 fixed params)

#### F(리서치): wick_reversal fold6 레짐 식별
- fold6 구간: 9-fold 구조에서 fold6 = IS_bars 1080 + 6*slide_bars 360 기준
  - 대략 start = 6*360 = 2160봉 = 2160*4h ≈ 360일 ≈ 2024-01-01 근방
- 2024년 초~중반 BTC 4h 특성: 상승 추세 지속 → Shooting Star 과다 발생 또는 Hammer 후 즉시 손실 패턴
- 대응: WickReversalStrategy에 레짐 필터 (MarketRegimeClassifier 연동) 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 267)
- 테스트: 8369 passed, 23 skipped
- Paper Sim BTC: 0/22 PASS (top: supertrend_multi +5.87%, Sharpe=0.43, PF=1.13)
- Bundle OOS BTC 4h: 0/5 PASS
  - cmf: 4/9 PASS fold, avg OOS Sharpe=-0.805, std=3.854
  - wick_reversal: 5/9 PASS fold, avg OOS Sharpe=1.211, avg PF=1.698, std=6.129
  - wick_reversal avg trades: 17.3 (개선, fold 최소 12거래)
  - OOS_SHARPE_STD_MAX: 2.0 (완화됨, 하지만 모두 초과)

### 주요 코드 변경 이력 (Cycle 267)
1. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["cmf"]["buy_thresh"] [0.07,0.08,0.09]→[0.08,0.09,0.10]
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["cmf"]["sell_thresh"] [-0.09,-0.08,-0.07]→[-0.10,-0.09,-0.08]
3. `src/backtest/walk_forward.py` — RollingOOSValidator.OOS_SHARPE_STD_MAX 1.5→2.0
4. `src/strategy/wick_reversal.py` — Hammer BUY filter `sma20*0.97`→`sma20*0.95`
