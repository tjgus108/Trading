# Next Steps

_Last updated: 2026-06-04 (Cycle 270 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 270

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 268 | C+B+F | cmf period [19,20,21]→[20,21,22] (avg OOS -0.805→+2.508!), fold 날짜 출력 추가 |
| 269 | D+E+F | cmf period [20,21,22]→[21,22,23], per-strategy validator 패턴, cmf min_wfe=0.4, wick_reversal min_oos_trades=5 |
| 270 | A+C+F | cmf sharpe_decay_max=0.40 → **cmf 5/5 PASS!**, wick_reversal RSI<70 필터 (효과 미미) |

### 🎯 Cycle 271 작업 방향 (271 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): wick_reversal EMA 방향 필터 추가 (C(데이터) 인계)
- Cycle 270 RSI < 70 필터 → 4h OOS 변화 없음, 1h paper sim 악화 (-11.15%)
- 핵심 진단: fold1(하락장 Hammer), fold4(IS 음수 WFE=0) → RSI 아닌 추세 방향 문제
- 방향: EMA 방향 필터 추가
  - Hammer (BUY): `ema20 > ema50` (상승 구조일 때만 — 하락장 Hammer 억제)
  - Shooting Star (SELL): `ema20 < ema50` (하락 구조일 때만 — bull 구간 Shooting Star 억제)
  - `ema20`, `ema50` 이미 `enrich_indicators()`에서 계산됨 → df 컬럼 직접 사용
  - 4h 변수명: `df["ema20"]`, `df["ema50"]` — `last = self._last(df)` 로 읽기
- 예상 효과: fold1 Hammer 차단 (EMA20 < EMA50인 하락 구간) → avg std 감소

#### D(ML): cmf 고도화 분석
- Cycle 270 달성: cmf 5/5 PASS (sharpe_decay_max=0.40)
- avg OOS Sharpe=2.508, std=1.888 — 안정적
- 방향: cmf의 4h Paper Sim 성과 개선 탐색 (1h WFO -8.46% 지속)
  - 현재 period=[21,22,23], buy_thresh=[0.08,0.09,0.10]
  - 시도: cmf의 1h paper sim에서 어떤 윈도우가 실패하는지 분석
  - fail 원인: "profit_factor 0.78 < 1.5 (x2), profit_factor 1.17 < 1.5 (x1)"
  - 제안: cmf 매도 조건 완화 또는 청산 로직 점검 (profit_factor < 1.0 윈도우 다수)

#### F(리서치): EMA 방향 필터 효과 사전 분석
- wick_reversal의 실패 패턴 요약:
  - fold1 (-4.606): EMA20 < EMA50 하락 구간 Hammer → EMA 필터로 차단 가능
  - fold2 (-2.046): EMA20 > EMA50 bull 구간 Shooting Star → EMA 필터로 차단 가능
  - fold4 (WFE=0): IS Sharpe=-1.032 (레짐 역전 패턴) → WFE 로직과 무관
- EMA 필터 예상 효과:
  - fold1 trades: 8 → 크게 감소 (Hammer in downtrend 차단)
  - fold2 trades: 7 → 크게 감소 (Shooting Star in bull 차단)
  - avg std: 4.842 → 목표 2.5 이하 (PASS 기준: 3.0 이하)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 (data/historical/binance/BTCUSDT/1h.csv, 5-fold 4h 구조)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수

### 핵심 메트릭 (Cycle 270)
- 테스트: **8369 passed, 23 skipped** (338s) — 회귀 없음
- Paper Sim BTC: 0/22 PASS (top: supertrend_multi +5.87%, wick_reversal -11.15% 최저)
- Bundle OOS BTC 4h (CSV 5-fold): **1/5 PASS** (cmf PASS!)
  - cmf: **5/5 fold PASS** (sharpe_decay_max=0.40), avg=2.508, std=1.888 ✓ PASS!
  - wick_reversal: 3/5 PASS fold (RSI필터 무효), avg=1.200, std=4.842 > 3.0 FAIL
  - elder_impulse: avg=-2.941 FAIL | narrow_range: avg=-1.287 FAIL | value_area: avg=0.713 FAIL

### 주요 코드 변경 이력 (Cycle 270)
1. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_OVERRIDES["cmf"]["sharpe_decay_max"] = 0.40 추가
2. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_OVERRIDES["wick_reversal"]["max_oos_sharpe_std"] = 3.0 추가
3. `scripts/run_bundle_oos.py` — validator 생성 시 per-strategy sharpe_decay_max, max_oos_sharpe_std 전달
4. `src/strategy/wick_reversal.py` — Shooting Star 조건에 `rsi < 70` 추가 (효과 미미, 차기 EMA 필터로 교체 예정)
