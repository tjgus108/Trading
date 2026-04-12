# Cycle 101 TODO

## 완료 (Cycle 100)
- volatility_cluster 개선 v2: -6.32% → -2.17% (필터 강화하나 여전히 손실)
  - 원본: vol_ratio 과다 의존으로 거짓 신호 다수
  - 개선: 로직 단순화하여 신호 정확도 향상 (코드 간결화)
  - 트레이드: 17개 → 35개 (신호 증가, 손실 감소)
  - 수익률 개선: -4.15%p 향상

## 완료 (Cycle 101)
- Signal.reasoning 최대 길이 500자 검증 추가 (`__post_init__`)
- test_signal_reasoning_max_length 테스트 추가 (6/6 passed)
- engulfing_zone 리서치 및 테스트 버그 수정 (11/11 passed)
  - 추세 필터(EMA50) + 위치 필터(Pivot Zone ±0.5%) 결합 구현 확인
  - Bearish engulfing zone 체크 버그: close_curr → open_curr 수정
  - 테스트 헬퍼 body ratio 버그 수정 (0.4 → 2.0)

## 리서치 결과 (2024-2025)
- 추세 필터 결합: win rate 50-70% → 유의미한 향상
- 위치 필터(지지/저항): Bearish Engulfing 72% 반전 성공률
- 횡보장에서 false signal 다수 → EMA50 추세 필터 필수
- 볼륨 급증 + RSI 조합이 false signal 최소화에 효과적

## 다음 작업
- engulfing_zone 백테스트 결과 검토 (-2.53% 개선 여부)
- Strategy agent 통합 테스트 (Phase L)
