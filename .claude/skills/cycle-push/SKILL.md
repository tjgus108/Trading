---
name: cycle-push
description: 사이클/세션 종료 시 origin/main까지 안전하게 푸시
disable-model-invocation: true
---

run_cycle.sh 또는 수동 세션 종료 시 커밋만 하고 push가 누락되는 일을 방지한다.
아래 순서대로 실행하고 결과를 보고:

1. `git status --short` — 변경/스테이징 상태 확인
2. 변경이 남아있으면 `git add -A && git commit -m "cycle: 자동 개선 결과 (post-session sweep) <UTC timestamp>"`
   - 단, `.env`, `config/secrets.json`, `.claude-state/live_paper_state.json`은 스테이징에서 제외 (gitignore로 관리)
3. `git rev-list --count @{u}..HEAD`로 미푸시 커밋 수 확인
4. 0이 아니면 `git push origin main`
5. push 실패 시 원인 간단히 보고 (auth / 네트워크 / non-fast-forward 여부)

금지:
- `--force` / `--force-with-lease` 단독 실행 금지 (사용자 승인 필요)
- main 외 브랜치를 임의로 덮어쓰지 말 것
- 스테이징에 secrets 포함되면 즉시 중단하고 사용자 알림
