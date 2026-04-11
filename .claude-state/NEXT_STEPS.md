# Cycle 97 — Backtest Agent Task (완료)

## 개선 완료: positional_scaling

**변경사항:**
- ATR(14) 기반 동적 풀백 범위: 고정 ±0.01~0.02 → `(ATR / EMA20) * 0.3`
- 더 유동적인 진입 조건으로 신호 빈도 증가
- 변동성이 높을 때는 범위 확대, 낮을 때는 축소

**테스트:**
- 모든 14개 테스트 통과

## 다음 Cycle
- Supertrend_multi 또는 다른 미개선 전략 선정
