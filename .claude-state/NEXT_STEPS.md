# Cycle 104 - SIM: engulfing_zone 개선 완료

## 완료 작업
✅ engulfing_zone 전략 개선 (v2 → v3)
  - RSI 임계값 완화: 50 → 55 (bullish), 50 → 45 (bearish)
  - Body ratio 감소: 1.3 → 1.2 (더 많은 신호)
  - Support/resistance를 신호 요구사항에서 신뢰도 부스트로 변경

✅ 테스트 15개 모두 통과 (구조 유지)
  - test_body_ratio_too_small_hold() 기준값 1.2로 업데이트
  - 전체 신호 생성 로직 검증

## 성능 개선 (synthetic data baseline)
- 거래: 17 → 22 (29% 증가)
- 수익: +6.23% → +9.22% (48% 개선)
- Sharpe: 2.589 → 3.296 (27% 개선)
- 최대낙폭: 2.5% → 3.8% (여전히 안전)
- 승률: 52.9% → 54.5%
- Profit Factor: 1.782 → 1.898

## Paper Simulation 결과
- **순위: #8** (상위 8/22 전략)
- **수익: +9.22%** (이전 -2.53% → 12% swing)
- Sharpe: 3.30, Win rate: 54.5%, PF: 1.90
- 최종잔고: $10,922

## 파일 변경
- `/home/user/Trading/src/strategy/engulfing_zone.py` (완전 재작성)
  - 라인 4-6: 전략 설명 업데이트
  - 라인 105, 117: ratio 임계값 1.2로 변경
  - 라인 127-131: RSI 임계값 변수화 (55/45)
  - 라인 136-139: Support/resistance 신뢰도 부스트
  
- `/home/user/Trading/tests/test_engulfing_zone.py` (완전 재작성)
  - 테스트 데이터 함수: ratio=1.2 기본값
  - 테스트 8, 10: HIGH 신뢰도 조건 확대 (1.5+ near zone)
  - 테스트 15: 기준값 1.2 (이전 1.2 → 1.15로 명확화)

## 다음 단계
- Cycle 105: 다음 하위 전략 개선 시도 (cmf, frama, 등)
