# Cycle 93 Summary - Sharpe vs Sortino 리서치

## [2026-04-11] Cycle 93 — Sharpe vs Sortino
- Sharpe는 총 변동성(상하 모두) 기준, Sortino는 하방 변동성만 사용 — 비대칭 수익 전략엔 Sortino가 더 정확
- 실전 봇 평가: Sharpe는 빠른 필터, Sortino는 크립토/고변동성 환경에서 보조 지표로 유용
- 현재 엔진(Sharpe>=1.0)은 합리적이나, 크립토 봇은 Sortino 추가 확인이 권장됨
- 단일 지표보다 Sharpe + Sortino + MDD + PF 조합이 실무 표준

## 이전 작업 (Cycle 92)
- `acceleration_band` 전략 필터 완화, Sharpe 0→0.78 개선
- 테스트 15/15 passed

## 다음 대상
- 엔진에 Sortino 보조 지표 추가 고려
- volatility_cluster 또는 positional_scaling 추가 개선
