# Current Cycle Briefing

_Cycle 266 완료 | 2026-06-03_

## 이번 사이클 요약

**카테고리**: B(리스크) + D(ML) + F(리서치)

### 완료된 작업

1. **DrawdownMonitor.set_sharpe_decay()** — 런타임 OOS decay 감지 포지션 축소
   - OOS/IS Sharpe < 0.50 → size_multiplier 0.5x
   - cmf fold 2/3 decay ratio 0.434/0.449 패턴 대응

2. **optimize_wick_reversal(timeframe)** — 4h봉 전용 min_volatility 그리드
   - 4h: [0.001, 0.002, 0.003] / 1h: [0.002, 0.003, 0.004]

3. **F(리서치)**: fee=0.055% 왕복 0.11% 구조, cmf IS/OOS decay 근본 원인(레짐 전환) 확인

### 시뮬 결과

| 지표 | 값 |
|------|-----|
| Bundle OOS PASS | 0/5 |
| cmf score | 80.6 (1위), std=1.888 |
| wick_reversal avg trades | 7.6 |
| 전체 테스트 | 8369 passed |

### 다음 우선순위 (Cycle 267)
1. cmf OOS std 1.888→<1.5: buy_thresh 그리드 이동 [0.08,0.09,0.10] 검토
2. wick_reversal SMA filter 완화: SMA20*0.97→0.95 또는 min_wick_ratio 0.50 검토
3. RollingOOSValidator.OOS_SHARPE_STD_MAX 완화 여부 판단 (1.5→2.0)
