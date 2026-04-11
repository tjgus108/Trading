# Cycle 28 - Config Validation 강화 완료

## 이번 작업 내용
`load_config()` 호출 시 위험 파라미터 자동 검증 추가.

**수정:**
1. `src/config.py`
   - L7: `import warnings` 추가
   - L67-84: `_validate_config()` 함수 신규 추가
     - `risk_per_trade > 0.1` → `ValueError`
     - `risk_per_trade > 0.05` → `UserWarning`
     - `max_position_size > 0.5` → `UserWarning`
   - L131: `_validate_config(cfg)` 호출

2. `tests/test_config.py`
   - L82-134: 검증 테스트 3개 추가

## 테스트 결과
6/6 passed (test_config.py)

## 다음 단계
- Cycle 29: connector retry 로직 검증 또는 새 전략 작업
