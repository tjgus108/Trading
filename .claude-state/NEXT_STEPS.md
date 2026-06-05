# Next Steps

_Last updated: 2026-06-05 (Cycle 276 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 276

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 274 | D+E+F | vol_mult 그리드 상향, supertrend_multi 파라미터화, cmf threshold 복원 |
| 275 | A+C+F | CMF rsi_max_buy 파라미터화, wick_reversal min_wick_ratio [0.55-0.65] 상향 |
| 276 | B+D+F | DrawdownStatus sharpe_decay_multiplier 추가, wick_reversal sma_sell_threshold 파라미터화 |

### 🎯 Cycle 277 작업 방향 (277 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): sma_sell_threshold 그리드 효과 검증
- sma_sell_threshold [1.01, 1.02, 1.03] 추가 완료 (Cycle 276)
- run_bundle_oos 재실행하여 fold6(2023-06~08) OOS Sharpe 개선 여부 확인
  - 기존: fold6 OOS=-12.365 (핵심 문제)
  - 목표: sma_sell_threshold=1.01 선택 시 SELL 신호 차단 → fold6 음의 Sharpe 개선
  - 위험: 거래 수 감소 (fold6 현재 24 trades → 과도 차단 시 <10)

#### D(ML): wick_reversal 종합 파라미터 효과 분석
- min_wick_ratio [0.55-0.65] + vol_mult [1.0-1.2] + sma_sell_threshold [1.01-1.03] 복합 효과
- WFO가 어떤 파라미터 조합을 선택하는지 확인
  - fold6 문제: sma_sell_threshold가 낮은 값 선택 → SELL 신호 차단
  - fold0 문제(OOS=-1.443): 2022-07~08 베어마켓, Hammer BUY 오신호 — sma_buy_threshold 고려
- 만약 OOS std > 5.0 지속이면: wick_reversal 번들에서 제외 + cmf+supertrend_multi 2전략 구조 검토

#### F(리서치): CMF 9-fold 구조 분석
- CMF가 9-fold에서 FAIL (5-fold에선 PASS) — 구조 차이 이해 필요
  - 9-fold: 2022 bear market fold 포함 → CMF가 2022에 취약
  - 5-fold: 2023-2024 only → CMF PASS 가능
  - 결론: CMF는 2022 같은 극단적 베어마켓에서 취약 (ema50 아래에서 신호 생성 어려움)
- 대응 방안 리서치:
  - 방안 1: CMF 번들 검증 기간을 2023 이후로 제한 (2022 제외 — 하지만 bias 위험)
  - 방안 2: CMF에 레짐 필터 추가 (불마켓 전용 전략으로 특화)
  - 방안 3: 9-fold PASS 기준 완화 (min_wfe 0.4 유지 + std 2.0→3.0 완화)

### ⚠️ 긴급 사항
- **wick_reversal fold6 OOS=-12.365**: sma_sell_threshold 파라미터화 효과 확인 필수
  - sma_sell_threshold=1.01 시 "close < SMA20 * 1.01" 조건 강화 → 불마켓 SELL 차단
  - 위험: 전체 SELL 신호 감소 → PASS folds(1,2,4,7,8)에서 trades 감소 가능
- **CMF 9-fold FAIL**: fold0,3,5,6 개선 방향 탐색 필요
  - fold5(2023-04~06 range), fold6(2023-06~08 bull) — CMF 레인지/초기불마켓 취약
  - rsi_max_buy 효과 미미 → buy_thresh 그리드 조정 또는 ema 필터 강화 검토

### 핵심 메트릭 (Cycle 276)
- 테스트: **8369 passed, 23 skipped** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - top: supertrend_multi +5.87%, cmf rank=13 AvgSharpe=-1.24
  - wick_reversal: rank=22, AvgSharpe=-2.79 (높은 파라미터 임계값, ETH/SOL 0거래)
- Bundle OOS BTC 4h (9-fold): **0/5 PASS**
  - cmf: FAIL avg=-0.805, std=3.854 (3/9 folds PASS: fold1,7,8)
  - wick_reversal: FAIL avg=1.289, std=6.085 (5/9 folds PASS, fold6=-12.365)

### 주요 코드 변경 이력 (Cycle 276)
1. `src/risk/drawdown_monitor.py` — DrawdownStatus에 sharpe_decay_multiplier 필드 추가
   - update() 반환 시 _sharpe_decay_mult 포함 → 모니터링 완전성 개선
2. `src/strategy/wick_reversal.py` — sma_sell_threshold 파라미터 추가 (기본값 1.03)
   - fold6 Shooting Star SELL 오신호 차단 목적 (추세장에서 SMA20 근접 요구 강화)
3. `src/backtest/walk_forward.py` — DEFAULT_GRIDS["wick_reversal"]에 sma_sell_threshold [1.01,1.02,1.03] 추가

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 9-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수
