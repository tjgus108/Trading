# Cycle 101 TODO

## 완료 (Cycle 100)
- volatility_cluster 개선 v2: -6.32% → -2.17% (필터 강화하나 여전히 손실)
  - 원본: vol_ratio 과다 의존으로 거짓 신호 다수
  - 개선: 로직 단순화하여 신호 정확도 향상 (코드 간결화)
  - 트레이드: 17개 → 35개 (신호 증가, 손실 감소)
  - 수익률 개선: -4.15%p 향상

## 다음 작업
- engulfing_zone 마지막 개선 (-2.53%)
- 또는 다른 전략 검토로 전환
- Strategy agent 통합 테스트 (Phase L)
