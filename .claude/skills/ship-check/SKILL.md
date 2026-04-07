---
name: ship-check
description: 커밋/배포 전 최종 체크리스트 실행
disable-model-invocation: true
---

순서대로 확인하고 결과만 출력:

1. `git diff --stat` — 변경 범위 확인
2. 관련 테스트 실행 (`pytest tests/` 또는 해당 파일)
3. `.env`, `secrets` 파일이 스테이징에 포함됐는지 확인
4. `src/risk/` 관련 변경이면 리스크 파라미터 재검토
5. `.claude-state/NEXT_STEPS.md` 업데이트

출력 형식:
- [PASS/FAIL] 항목명
- 실패 항목만 상세 설명
