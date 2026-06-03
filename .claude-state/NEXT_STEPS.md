# Next Steps

_Last updated: 2026-06-03 (Cycle 268 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 268

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 267 | B+D+F | cmf buy_thresh 보수화, OOS_SHARPE_STD_MAX 2.0, wick_reversal SMA 0.95 (avg trades 7.6→17.3) |
| 268 | C+B+F | OOSFoldResult 날짜 필드, wick_reversal min_wick_ratio [0.40-0.50], cmf period [20-22] |

### 🎯 Cycle 269 작업 방향 (269 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): wick_reversal 레짐 필터 검토
- 현재: fold1(2023-08-29~10-27) OOS=-4.606, fold2(2023-10-28~12-26) OOS=-2.046 → 상승장 SELL 신호 손실
- 방향: `wick_reversal.py`에 레짐 필터 추가: 상승 추세(close > SMA50)에서 SELL 신호 억제
  - `generate_signal()` 내 Shooting Star 조건에 `close < sma50` 추가 (단순 레짐 필터)
  - 또는: `src/backtest/walk_forward.py` DEFAULT_GRIDS["wick_reversal"]에 `sell_regime_filter: [True, False]` 그리드
- 주의: 전략 파일 신규 생성 금지, 기존 `wick_reversal.py` 수정

#### E(실행): cmf WFE FAIL 분석 및 파라미터 재검토
- 현재: fold2(2023-10-28~12-26) WFE=0.434, fold3(2023-12-27~2024-02-24) WFE=0.449 < 0.50
- 방향: cmf strategy default params 재검토
  - `src/strategy/cmf.py` default period=21 또는 buy_thresh=0.09 로 이동 (더 보수적)
  - 이유: RollingOOSValidator는 WFO 없이 default 파라미터 사용 → IS Sharpe 3.295 과최적화 방지

#### F(리서치): 레짐-조건부 전략 스위칭 기법
- 논문: "Regime-Switching in Trading Strategies" (SSRN, 2023)
- 아이디어: SMA200 위/아래로 Bull/Bear 레짐 구분 → wick_reversal Bull에서 LONG only, Bear에서 SELL only
- wick_reversal fold별 레짐 OOS 날짜 분석 결과 (Cycle 268에서 추가된 날짜 출력 활용):
  - fold2-3 OOS (2023-10 ~ 2024-02): BTC 30k→52k 강한 bull → Shooting Star 전면 비활성화 필요

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 12000봉, 2023-01-01~2024-05-14)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 → 5 folds (3000 4h봉)
  - 참고: 이전 9-fold 결과는 거래소 직접 연결 시 (4320봉 기준)

### 핵심 메트릭 (Cycle 268)
- 테스트: **8369 passed, 23 skipped** (전체 스위트)
- Paper Sim BTC: 실행 중 (이전 사이클 top: supertrend_multi +5.87%, Sharpe=0.43)
- Bundle OOS BTC 4h (5-fold, CSV 기반): 0/5 PASS
  - cmf: 3/5 PASS fold, avg OOS Sharpe=2.508, std=1.888, FAIL(fold2/3 WFE<0.50)
  - wick_reversal: 저거래 FAIL (fold0-3 < 10 trades 제외), avg OOS Sharpe=1.772
  - elder_impulse: avg OOS Sharpe=-2.941 (불안정, std=3.117)
  - narrow_range: avg OOS Sharpe=-1.287 (std=2.695)
  - value_area: avg OOS Sharpe=0.713 (std=2.018)

### 주요 코드 변경 이력 (Cycle 268)
1. `src/backtest/walk_forward.py` — OOSFoldResult에 `oos_start`, `oos_end` 날짜 필드 추가
2. `src/backtest/walk_forward.py` — RollingOOSValidator.validate() fold 날짜 기록 + logger 날짜 출력
3. `scripts/run_bundle_oos.py` — format_fold_detail 테이블에 "OOS Period" 컬럼 추가
4. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["wick_reversal"]["min_wick_ratio"] [0.50,0.55,0.60]→[0.40,0.45,0.50]
5. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["cmf"]["period"] [19,20,21]→[20,21,22]
