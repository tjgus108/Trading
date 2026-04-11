# Cycle 37 - Category D: ML & Signals 완료

## [2026-04-11] Cycle 37 — LLMAnalyst 프롬프트 개선
- `analyze_signal`에 `research_insights` 파라미터 추가 (200자 자동 truncate)
- `_build_prompt`에 "Historical Insights" 섹션 선택적 삽입
- `_parse_response` 추가: 마크다운 제거 + 최대 3문장 제한
- 테스트 3개 추가 (총 13개, 전체 통과)

## 파일 변경
- `src/alpha/llm_analyst.py`
- `tests/test_llm_analyst.py`

## 다음 단계
- Cycle 38 준비

---
# Cycle 37 - Category F: Research 완료

## [2026-04-11] Cycle 37 — ccxt Best Practices
- `enableRateLimit=True` 필수 설정, `maxRequestsQueue` 기본 1000 (초과 시 throttle 에러)
- sync 버전은 멀티스레드 비안전 — 동시 처리 시 async(ccxt.pro) 사용 권장
- 에러 핸들링: try-catch + ccxt 계층형 예외(NetworkError, ExchangeError 등) 구조적 처리
- exchange 인스턴스 재사용 필수 (rate limit 상태 유지)

## 파일 변경
- 없음 (리서치 전용)

## 다음 단계
- Cycle 38 준비
