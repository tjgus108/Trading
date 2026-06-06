# Next Steps

_Last updated: 2026-06-06 (Cycle 279 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 279

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 277 | B+D+F | WFE 레짐 전환 임계값 2.0→1.5, BUNDLE_STRATEGY_INIT_PARAMS 추가 |
| 278 | C+B+F | wick_reversal has_momentum 필터, Bundle에서 wick_reversal→supertrend_multi 교체 |
| 279 | D+E+F | supertrend_multi atr_threshold_max=2.0 추가, atr_threshold 0.9→0.7, avg 1.699→2.266 |

### 🎯 Cycle 280 작업 방향 (280 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): supertrend_multi fold4 원인 깊이 분석
- fold4 (2024-02~04 BTC ATH, $40k→$73k): OOS=-4.239, trades=16
  - `atr_threshold_max=2.0` 적용 후에도 개선 없음 → ATR ratio가 2.0 미만이었을 것
  - 실제 분석 방법:
    1. CSV 데이터(data/historical/binance/BTCUSDT/1h.csv)에서 2024-02~04 구간 ATR ratio 계산
    2. 해당 구간에서 supertrend_multi가 어떤 신호를 발생시키는지 확인
  - 가설: BTC 상승 구간에서 단기 조정 시 supertrend가 bearish 전환 → SELL → 반등으로 손실
  - 개선 방안:
    1. **장기 EMA 필터 추가**: EMA50 또는 EMA200 위에 있을 때 SELL 차단 (추세 방향 일치 확인)
    2. **atr_threshold_max 낮추기**: 2.0→1.5 테스트 (ATH 구간에서도 차단 효과 발생하는지)
    3. **볼륨 확인 강화**: HIGH confidence만 거래 (MEDIUM 무시)

#### C(데이터): supertrend_multi 4h fold4 ATR ratio 실측
- BTC 1h CSV → 4h 리샘플링 → 2024-02~04 구간 ATR ratio 계산
- `cur_atr / avg_atr` 분포 확인: max ratio가 2.0을 초과하는지 확인
- 결과에 따라 atr_threshold_max 조정 (2.0→1.5 또는 유지)

#### F(리서치): 추세 추종 전략 SELL 차단 기법 리서치
- ATH/강한 상승 구간에서 추세 추종 전략의 SELL 오신호 방지 방법:
  1. 장기 이평선 필터 (close < EMA200일 때만 SELL)
  2. ADX 필터 (ADX > 25인 강한 추세 구간에서 SELL 차단)
  3. 레짐 감지 (HMM/rule-based): bull 레짐에서 SELL 억제

### ⚠️ 긴급 사항
- **supertrend_multi fold4 핵심 문제**: 4/5 fold PASS이지만 fold4 때문에 FAIL — fold4 해결 시 PASS 달성 가능
- **Bundle OOS 목표**: supertrend_multi PASS → cmf+supertrend_multi 2개 PASS 달성
- **std 목표**: supertrend_multi std=3.792 → 목표 < 2.0 (fold4 개선 시 자연히 달성)

### 핵심 메트릭 (Cycle 279)
- 테스트: **8369 passed** — 회귀 없음
- Paper Sim BTC 1h: 0/22 PASS
  - rank1: supertrend_multi +6.73% (AvgSharpe=0.60) ← Cycle 278 대비 개선 (+5.87%, 0.43)
  - rank2: price_cluster +2.50% (AvgSharpe=0.40)
- Bundle OOS BTC 4h (5-fold, Cycle 279):
  - cmf: **PASS** avg=2.508, std=1.888 ← 7회 연속 PASS
  - supertrend_multi: FAIL avg=2.266 (↑1.699), std=3.792 (fold4: OOS=-4.239, 4/5 PASS)
  - elder_impulse: FAIL avg=-2.941, std=3.117
  - narrow_range: FAIL avg=-1.287, std=2.695
  - value_area: FAIL avg=0.713, std=2.018

### 주요 코드 변경 이력 (Cycle 279)
1. `src/strategy/supertrend_multi.py` — atr_threshold_max 파라미터 추가
   - `__init__`: `atr_threshold=0.7, atr_threshold_max=2.0` (기본값)
   - `_atr_filter_pass()`: `self.atr_threshold <= ratio <= self.atr_threshold_max` 범위 체크
2. `src/backtest/walk_forward.py` — DEFAULT_GRIDS 확장
   - `atr_threshold_max: [1.5, 2.0, 3.0]` 추가
   - `optimize_supertrend_multi` factory에 `atr_threshold_max` 연결
3. `scripts/run_bundle_oos.py` — BUNDLE_STRATEGY_INIT_PARAMS 추가
   - `supertrend_multi: {"atr_threshold": 0.7, "atr_threshold_max": 2.0}`

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: synthetic CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조)
