# Cycle 119: htf_ema 2차 강화

## 실행 결과

### 수정 사항
1. RSI extreme 필터 추가: BUY RSI <= 75, SELL RSI >= 25
2. Cross 거리 필터 강화: 0.5배 변동성 필요 (이전 0.3배)
3. 볼륨 가중치: 거래량 > 1.3배 시 신뢰도 상향

### 백테스트 결과
```
Before (Cycle 87): Return +1.79%, Sharpe 0.60, PF 1.12 (43 trades) ❌
After:             Return +2.18%, Sharpe 0.71, PF 1.14 (42 trades) ❌
```

### 실패 원인 분석
- **Sharpe 0.71** (필요: >= 1.0) — 변동성 대비 수익 부족
- **Profit Factor 1.14** (필요: >= 1.5) — 손실 거래 너무 많음
- 42개 거래 중 손실 거래 비율이 높아 risk-adjusted return 약함

### 근본 문제
HTF EMA + EMA9 cross 조합은 매우 기본적 신호.
과도한 false break 발생. 추가 필터만으로는 부족.

### 전략 상태
**FAIL** - 최소 임계값 미충족
- Sharpe Ratio: 0.71 < 1.0
- Profit Factor: 1.14 < 1.5

### 다음 단계 (향후 개선)
1. 추가 지표 검토 (MACD, CCI 등)
2. 엔트리 신호 재설계 (현재는 이미 강한 필터 적용)
3. 포지션 관리 (동적 손절 개선)
4. 차트 패턴 통합

## 시스템 상태
- 테스트: ✅ 전체 통과 (21/21)
- 전략 로드: ✅ PASS 22개 유지

---
Updated: 2026-04-12 13:09
