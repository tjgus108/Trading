# Cycle 96 — Data Agent Task

## 완료 항목
- News monitor 중복 감지 강화 (Cycle 49 → 개선)
- `_get_title_hash()`: 내부 공백 정규화 추가
- 테스트 추가: `test_duplicate_detection_mixed_case_and_whitespace()`
- 전체 테스트: 8/8 PASS

## 수정 내역
### src/data/news.py
- `_get_title_hash()`: `re.sub(r'\s+', ' ')` 추가로 중복 내부 공백 정규화
  대소문자 + 공백 차이 무관하게 중복 감지

## 다음
- Cycle 97: 저성능 전략 개선 (dema_cross/positional_scaling 중 1개)
