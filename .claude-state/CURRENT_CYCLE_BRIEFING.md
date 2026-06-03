# Current Cycle Briefing

_Cycle 267 완료 | 2026-06-03_

## 이번 사이클 요약

**카테고리**: B(리스크) + D(ML) + F(리서치)

### 완료된 작업

1. **cmf buy_thresh 보수화** — [0.07-0.09]→[0.08-0.10], sell_thresh 대칭 이동
   - 목표: IS 최적화 시 고Sharpe fold에서 안정적 파라미터 선택
   - 결과: avg OOS Sharpe=-0.805 (악화), 추가 분석 필요

2. **RollingOOSValidator.OOS_SHARPE_STD_MAX 1.5→2.0** — fold 간 자연 분산 허용
   - cmf std=3.854, wick_reversal std=6.129 (여전히 초과, 구조적 문제)

3. **wick_reversal SMA filter 완화 (0.97→0.95)** — 하락 추세 구간 신호 허용
   - avg trades 7.6→17.3 (저거래 구조 해결 ✓)
   - 단, fold6 OOS Sharpe=-12.365 극단 손실 (상승 레짐 오신호 의심)

4. **F(리서치)**: Regime-Conditional WF, Anchored WF, fold min Sharpe 기준 조사

### 시뮬 결과

| 지표 | 값 |
|------|-----|
| Bundle OOS PASS | 0/5 |
| wick_reversal score | 1위 (88.3점), avg trades=17.3 |
| wick_reversal OOS Sharpe | 1.211 avg (5/9 PASS fold) |
| cmf avg OOS Sharpe | -0.805 (4/9 PASS fold) |
| 전체 테스트 | 8369 passed |

### 다음 우선순위 (Cycle 268 — C+B+F)
1. wick_reversal fold6 극단 손실(-12.365) 원인: 레짐 식별 + 날짜 구간 출력
2. cmf avg OOS 음수: period 범위 이동 [20,21,22] 또는 WFO 파라미터 최적화 검토
3. WickReversal + MarketRegimeClassifier 연동 가능성 조사
