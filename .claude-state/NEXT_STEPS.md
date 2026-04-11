# Cycle 36 - Category A: Quality Assurance 완료

## 완료 내용
- **Monte Carlo 경계 조건 테스트 추가** (`/home/user/Trading/tests/test_monte_carlo.py`)
  - 10개 테스트 추가: 정상 케이스, 빈 데이터, 단일 거래, NaN, 음수 수익률, seed 재현성 등
  - 테스트 커버 범위: 정상 흐름, 엣지 케이스, 파라미터 변동

## 버그 수정
- `src/backtest/monte_carlo.py` - Block Bootstrap 및 계산 메서드 강화
  - `_block_bootstrap()`: 빈 배열 처리 추가 (n==0 또는 target_len==0)
  - `_sharpe()`: 빈 배열에서 NaN 반환
  - `_max_drawdown()`: 빈 배열에서 NaN 반환

## 파일 변경
- `/home/user/Trading/tests/test_monte_carlo.py` (신규)
- `/home/user/Trading/src/backtest/monte_carlo.py` (버그 수정)

## 테스트 결과
- `test_monte_carlo.py`: 10/10 PASS
- 기존 통합 테스트 영향 없음 (호환성 유지)

## 다음 단계
- Cycle 37 준비
