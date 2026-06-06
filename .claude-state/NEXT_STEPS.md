# Next Steps

_Last updated: 2026-06-06 (Cycle 278 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 278

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 276 | B+D+F | DrawdownStatus sharpe_decay_multiplier 추가, wick_reversal sma_sell_threshold 파라미터화 |
| 277 | B+D+F | WFE 레짐 전환 임계값 2.0→1.5, BUNDLE_STRATEGY_INIT_PARAMS 추가 |
| 278 | C+B+F | wick_reversal has_momentum 필터, Bundle에서 wick_reversal→supertrend_multi 교체 |

### 🎯 Cycle 279 작업 방향 (279 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): supertrend_multi fold4 실패 원인 분석 및 개선
- fold4 (Feb-Apr 2024: BTC ATH 구간) OOS=-4.239 → 핵심 문제
  - 이 기간 BTC: ~40k → ~73k (강한 상승추세)
  - supertrend_multi가 추세 추종임에도 OOS 손실 → whipsaw 또는 SELL 오신호 의심
  - 조사 방향:
    1. fold4 IS구간 (Aug-Oct 2023)에서 IS_Sharpe=1.59 → 좋음
    2. fold4 OOS (Feb-Apr 2024)에서 16 trades → 충분한 거래
    3. ATR 필터 작동: 이 기간 ATR이 급등하여 `cur_atr >= avg_atr * 0.9` 통과 → 신호 과다 발생?
  - 개선 방안:
    - `atr_threshold` 상향 (0.9→1.2): ATR이 MA의 120% 이상일 때만 신호 (고변동성 신호 감소)
    - 또는 상한도 추가: `atr_threshold_max = 2.0` (ATR이 너무 높으면 신호 차단)

#### E(실행): supertrend_multi 4h 거래 빈도 문제
- fold1(7), fold2(3), fold3(3): 매우 낮은 trades → 신호 생성 희소
  - 현재 min_oos_trades=3 오버라이드로 집계는 가능하지만 실전에서는 거래 기회 부족
  - 개선 방안:
    1. `atr_threshold` 하향 (0.9→0.7): 더 많은 신호 허용
    2. 또는 trend_confirmation_pass 완화: 현재 "마지막 2봉 모두 같은 방향" → "1봉만"으로 완화
  - 주의: 거래 빈도와 신호 품질의 trade-off 존재

#### F(리서치): supertrend_multi ATR 임계값 최적화 리서치
- 현재 그리드: `"atr_threshold": [0.7, 0.8, 0.9]` in DEFAULT_GRIDS
- 추가 고려: 상한 임계값 (ATR 급등 시 신호 차단)
- 2024년 BTC ATH 구간(Feb-Apr) 특성: 고변동성 + 강한 상승 → supertrend signal quality 분석

### ⚠️ 긴급 사항
- **supertrend_multi fold4 분석 우선**: fold3 WFE<0.5도 문제이지만, fold4 OOS=-4.239가 avg_sharpe를 끌어내림
- **Bundle OOS 목표**: cmf 외 1개 전략 PASS → 현재 supertrend_multi가 가장 근접 (avg=1.699)
- **std 기준**: supertrend_multi std=3.769 → 목표 < 2.0 (fold4 개선 시 달성 가능)

### 핵심 메트릭 (Cycle 278)
- 테스트: **8369 passed** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - rank1: supertrend_multi +5.87% (AvgSharpe=0.43)
  - wick_reversal: -12.97% (최하위, has_momentum 필터 후에도 동일 → 근본적 시장 적합성 부재)
- Bundle OOS BTC 4h (5-fold, Cycle 278):
  - cmf: **PASS** avg=2.508, std=1.888 ← 유일한 PASS
  - supertrend_multi: FAIL avg=1.699, std=3.769 (3/5 PASS, fold4: OOS=-4.239)
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 278)
1. `src/strategy/wick_reversal.py` — Hammer BUY에 14봉 양(+) 모멘텀 필터 추가
   - `ref_close_14 = df["close"].iloc[-trend_lookback-1]` 계산
   - `has_momentum = close > ref_close_14` 조건
   - hammer 조건에 `has_momentum and` 추가
2. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGIES 교체
   - wick_reversal → supertrend_multi (3회 연속 FAIL, std=4.842 개선 불가)
   - BUNDLE_STRATEGY_OVERRIDES에 supertrend_multi: min_oos_trades=3 추가
   - BUNDLE_STRATEGY_INIT_PARAMS의 wick_reversal 항목 삭제

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
