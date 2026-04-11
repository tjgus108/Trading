#!/bin/bash
# 5시간마다 Claude Code 세션을 열어 cycle_dispatcher → agent 작업 → commit+push 진행
#
# cron 등록 예시:
#   0 */5 * * * cd ~/Trading && bash scripts/run_cycle.sh >> /tmp/cycle.log 2>&1

set -e

cd "$(dirname "$0")/.."

echo "==================================="
echo "🔄 Cycle run: $(date -u +'%Y-%m-%d %H:%M:%SZ')"
echo "==================================="

# 1. 최신 코드 pull
git fetch origin main
git checkout main
git pull origin main

# 2. 이전 사이클 완료 확인 (브리핑 파일 존재 여부)
# CYCLE_STATE.txt는 이미 다음 사이클 번호를 가리키고 있음

# 3. 새 사이클 브리핑 생성
python3 scripts/cycle_dispatcher.py

# 4. Claude Code 세션 실행 (브리핑을 읽고 agent 배정)
#    --permission-mode=acceptEdits : 확인 없이 진행
#    --dangerously-skip-permissions : 완전 자동 (주의)
PROMPT="$(cat <<'EOF'
.claude-state/CURRENT_CYCLE_BRIEFING.md를 읽고 지시사항대로 진행해.

핵심:
1. 브리핑에 나열된 3개 카테고리를 Agent tool로 병렬 실행
2. 각 에이전트에게 명확한 작업 지시 (focus 항목 중 1~2개 실제 개선)
3. F 카테고리 (Research)는 트레이딩봇 실패/성공 케이스 리서치 필수 포함
4. 모든 에이전트 완료 후:
   - .claude-state/WORKLOG.md 업데이트
   - STATUS.md 업데이트
   - .claude-state/NEXT_STEPS.md 업데이트
5. git add -A && git commit -m "[Cycle N] 요약" && git push origin main
6. 완료 후 종료

금지: 새 전략 파일 생성, 한 카테고리 집중, 실패 사례 리서치 스킵
EOF
)"

# Claude CLI 실행 (home laptop에서 실제 동작)
claude -p "$PROMPT" \
    --allowedTools "Edit,Write,Read,Bash,Glob,Grep,Agent" \
    --permission-mode=acceptEdits \
    || echo "Claude session failed — check logs"

echo "==================================="
echo "✅ Cycle completed: $(date -u +'%Y-%m-%d %H:%M:%SZ')"
echo "==================================="
