# Cycle 38 - Category F: Research 완료

## [2026-04-11] Cycle 38 — Kimchi Premium
- 2024-2025: 프리미엄 2~5%로 압축, 2024년 말 역전(디스카운트) 발생, 2025년 말 -0.18% 디스카운트 고착
- 직접 차익거래는 외환거래법(Foreign Exchange Transactions Act) + VAPUA KYC/AML로 사실상 불가 (24-72시간 출금 지연, 기관 선점)
- 실용 전략: 프리미엄 -2% 이하 시 DCA 2-3배 집중 매수 (백테스트 12개월 수익률 187% vs 일반 DCA 64%)
- 트래커: CoinGlass, CryptoQuant

## 파일 변경
- 없음 (리서치 전용)

## 다음 단계
- Cycle 39 준비

---
# Cycle 38 - Category A: Quality Assurance 완료

## [2026-04-11] Cycle 38 — Monte Carlo 빈 배열 버그 회귀 테스트 추가
- `_block_bootstrap` 메서드의 빈 배열 처리 로직(Cycle 36 수정) 검증
- 회귀 테스트 3개 추가:
  1. `test_monte_carlo_block_bootstrap_empty_array` - 빈 배열 직접 처리
  2. `test_monte_carlo_block_bootstrap_zero_target_len` - target_len=0 처리
  3. `test_monte_carlo_run_with_many_nans_resulting_empty` - 대부분 NaN인 Series 처리
- 전체 테스트 13개 통과

## 파일 변경
- `tests/test_monte_carlo.py` - 회귀 테스트 3개 추가

## 다음 단계
- Cycle 39 준비
