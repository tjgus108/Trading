# Cycle 97 — Backtest Agent Task

## 시도한 개선
- **dema_cross**: +9.44% baseline, PF 1.38 (< 1.5 threshold)
  - 시도: RSI필터, ATR거리, 모멘텀, 가격방향, 볼륨
  - 결과: 모든 필터가 신호/이익 감소 → 구조적 한계

## 결론
- `dema_cross`: FAIL (PF < 1.5)
- 단순 필터로는 개선 불가능
- 전략 재설계 또는 퇴출 필요

## 다음
- Cycle 98: 새로운 저성능 전략 선정
