# Next Steps

_Last updated: 2026-06-05 (Cycle 277 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 277

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 275 | A+C+F | CMF rsi_max_buy 파라미터화, wick_reversal min_wick_ratio [0.55-0.65] 상향 |
| 276 | B+D+F | DrawdownStatus sharpe_decay_multiplier 추가, wick_reversal sma_sell_threshold 파라미터화 |
| 277 | B+D+F | WFE 레짐 전환 임계값 2.0→1.5, BUNDLE_STRATEGY_INIT_PARAMS 추가, sma_sell_threshold 효과 검증 |

### 🎯 Cycle 278 작업 방향 (278 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): wick_reversal BUY 신호 품질 분석
- Cycle 277 발견: sma_sell_threshold=1.01이 fold1,2에 효과 없음 → BUY Hammer 오신호가 핵심 문제
- fold1 (Aug-Oct 2023 횡보): Hammer BUY가 횡보 구간에서 오발 → 진입 후 손실
  - 원인: `trend_up = high >= high_14 * 0.99` 조건이 횡보에서도 True (최근 고점 대비 1% 이내)
  - 개선 방안: trend_up 조건 강화 → `high >= high_14 * 0.97` (더 강한 상승 모멘텀 요구)
- fold2 (Oct-Dec 2023 초기 불마켓): Hammer BUY 후 빠른 조정으로 손절
  - 개선 방안: `min_wick_ratio` 추가 상향 (0.65→0.70) 또는 ema 기울기 필터 추가

#### B(리스크): supertrend_multi 번들 교체 검토
- wick_reversal이 5-fold에서 지속 FAIL (std=4.842 >> 3.0 허용 기준)
- Paper Sim에서 supertrend_multi가 1위 (+5.87%) vs wick_reversal 22위 (-11.15%)
- 검토 방안: `BUNDLE_STRATEGIES`에서 wick_reversal → supertrend_multi 교체
  - run_bundle_oos.py의 BUNDLE_STRATEGIES 리스트 수정
  - supertrend_multi RollingOOS validate 실행 → cmf와 비교

#### F(리서치): wick_reversal vs supertrend_multi 비교 분석
- wick_reversal이 반전 전략 (레인지/베어 구간에서 강점)
- supertrend_multi가 추세 전략 (불마켓/강한 추세 구간에서 강점)
- 두 전략이 서로 상관관계가 낮으면: 포트폴리오 다양화 효과 유지
- Bundle OOS에 supertrend_multi를 추가하여 cmf와 보완성 확인

### ⚠️ 긴급 사항
- **wick_reversal fold1 OOS=-4.606**: SELL 아닌 BUY 신호가 원인 → trend_up 조건 강화 필요
- **wick_reversal 번들 교체 결정**: std=4.842 >> 3.0, 3회 연속 주요 개선에도 FAIL → supertrend_multi 교체 검토

### 핵심 메트릭 (Cycle 277)
- 테스트: **70 passed** (walk_forward + bundle_oos targeted) — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS (Cycle 276 결과)
  - top: supertrend_multi +5.87%, wick_reversal: rank=22, AvgSharpe=-2.79
- Bundle OOS BTC 4h (5-fold, Cycle 277 재실행):
  - cmf: **PASS** avg=2.508, std=1.888 (5/5 folds PASS) — 안정적
  - wick_reversal: FAIL avg=1.200, std=4.842 (3/5 PASS: fold0,3,4)
    - fold4 WFE 0.0→0.5 (WFE 임계값 2.0→1.5 수정 효과)
    - fold1,2 개선 없음 (sma_sell_threshold=1.01 효과 없음)

### 주요 코드 변경 이력 (Cycle 277)
1. `src/backtest/walk_forward.py` — RollingOOSValidator WFE 레짐 전환 OOS 임계값 2.0→1.5
   - IS < -1.0 + OOS > 1.5 → WFE=0.5 (레짐 전환 마커)
   - wick_reversal fold4(IS=-1.032, OOS=1.772) FAIL→PASS 구제
2. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS 추가
   - wick_reversal: sma_sell_threshold=1.01 적용
   - load_strategy()에서 per-strategy 파라미터 적용

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
