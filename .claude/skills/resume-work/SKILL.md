---
name: resume-work
description: 저장된 상태 파일을 읽고 미완료 작업만 이어서 진행
disable-model-invocation: true
---

1. `.claude-state/NEXT_STEPS.md`와 `.claude-state/WORKLOG.md`를 읽는다.
2. `git status`로 변경사항 확인.
3. 미완료 작업만 이어서 진행. 완료된 것은 건드리지 않는다.
4. 전체 레포를 다시 스캔하지 않는다. 필요한 파일만 읽는다.
5. 작업 완료 후 `.claude-state/NEXT_STEPS.md` 업데이트.
