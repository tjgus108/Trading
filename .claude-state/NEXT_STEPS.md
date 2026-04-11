# Cycle 25 - Orchestrator health_check 연동 완료

## 이번 작업 내용
`src/orchestrator.py` run_once() 내 health check 버그 수정 (기존 코드 이미 있었으나 UnboundLocalError로 동작 불가).

**버그:** L868에 `from src.pipeline.runner import PipelineResult` 지역 import가 있어 함수 스코프에서 PipelineResult를 로컬 변수로 취급. drawdown 블록이 실행 안 되면 unbound → health check 블록의 `return PipelineResult(...)` 에서 UnboundLocalError 발생 → except로 삼켜져 pipeline 계속 실행.

**수정:**
1. `src/orchestrator.py` L868: 중복 `from src.pipeline.runner import PipelineResult` 제거 (top-level import 사용)
2. `src/orchestrator.py` L903: notes 문자열 `"DataFeeds all_disconnected"` → `"all_feeds_disconnected"` (테스트 기대값 일치)

**동작:**
- `all_feeds_disconnected` → pipeline SKIP, BLOCKED 반환
- `operating_in_degraded_mode` → WARNING 로그 후 pipeline 계속

## 테스트 결과
```
tests/test_orchestrator.py: 18 passed in 1.51s
```

## 다음 단계
- BaseStrategy.generate()에서 is_active_session() 활용해 신호 강도 조정
- 아시아 세션 진입 스킵: confidence *= 0.5 or action → HOLD
- Health check: data-agent 초기화 시 자동 feed 등록
- Telegram 알림 컨텍스트 강화 (에러/경고 시 context 포함)
