#!/bin/bash
# 5시간마다 Claude Code 세션을 열어 cycle_dispatcher → agent 작업 → commit+push 진행
#
# cron 등록 예시 (경로는 실제 프로젝트 위치로):
#   0 */5 * * * cd ~/Desktop/AgentTest/Trading && bash scripts/run_cycle.sh >> /tmp/cycle.log 2>&1
#
# macOS 주의:
#   1) 시스템 설정 → 개인정보보호 → 전체 디스크 접근 권한에 /usr/sbin/cron 추가
#   2) chmod +x scripts/run_cycle.sh
#   3) claude/python3/git 경로는 아래 PATH export로 보정

set -e

# cron 환경의 최소 PATH 보정 (homebrew + 시스템 + 사용자 bin)
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/bin:$PATH"

cd "$(dirname "$0")/.."

# Python 인터프리터 선택: 프로젝트 venv 우선, 없으면 시스템 python3
if [ -x ".venv/bin/python3" ]; then
    PY_BIN=".venv/bin/python3"
elif [ -x ".venv/bin/python" ]; then
    PY_BIN=".venv/bin/python"
else
    PY_BIN="python3"
fi
echo "[PY] Using interpreter: $PY_BIN ($($PY_BIN --version 2>&1))"

# .env 자동 로드 (EXCHANGE_API_KEY, TELEGRAM_BOT_TOKEN 등)
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

echo "==================================="
echo "🔄 Cycle run: $(date -u +'%Y-%m-%d %H:%M:%SZ')"
echo "==================================="

# 1. 최신 코드 pull
# 1-pre: 이전 사이클이 중단돼 남긴 변경사항 자동 커밋 (pull --rebase 실패 방지)
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "--- 이전 사이클 잔재 감지 → 자동 커밋 후 pull 진행 ---"
    git add -A
    git commit -m "chore: pre-cycle cleanup (auto) $(date -u +'%Y-%m-%dT%H:%MZ')" || true
fi
git fetch origin main
git checkout main
git pull origin main

# 2. Paper Simulation (실제 Bybit 데이터 수익률 테스트)
# - 리포트가 없거나, 24시간 이상 지났거나, --force 옵션 시 재실행
# - 그 외에는 스킵 (6시간마다 재실행은 rate-limit/CPU 낭비)
REPORT=".claude-state/PAPER_SIMULATION_REPORT.md"
FORCE_SIM=false
[ "${1:-}" = "--force" ] && FORCE_SIM=true

RUN_SIM=false
if [ ! -f "$REPORT" ] || ! grep -q "Bybit BTC/USDT" "$REPORT" 2>/dev/null; then
    RUN_SIM=true
    echo "--- Paper Simulation: 리포트 없음/마커 없음 → 실행 ---"
elif $FORCE_SIM; then
    RUN_SIM=true
    echo "--- Paper Simulation: --force 플래그 → 강제 실행 ---"
elif [ -n "$(find "$REPORT" -mmin +1440 2>/dev/null)" ]; then
    RUN_SIM=true
    echo "--- Paper Simulation: 리포트 24h 초과 → 재실행 ---"
else
    AGE_MIN=$(( ($(date +%s) - $(stat -f %m "$REPORT" 2>/dev/null || stat -c %Y "$REPORT")) / 60 ))
    echo "--- Paper Simulation: 최근 실행 ${AGE_MIN}분 전 → 스킵 (24h 주기) ---"
fi

if $RUN_SIM; then
    "$PY_BIN" scripts/paper_simulation.py || echo "Paper sim failed — continuing cycle"
    if [ -f "$REPORT" ] && grep -q "Bybit" "$REPORT" 2>/dev/null; then
        git add "$REPORT" .claude-state/ 2>/dev/null || true
        git commit -m "paper: 실제 Bybit 데이터 시뮬레이션 결과 ($(date -u +'%Y-%m-%dT%H:%MZ'))" || true
        git push origin main || echo "paper sim push 실패 — 나중에 sweep에서 재시도"
    fi
fi

# 3. 이전 사이클 완료 확인 (브리핑 파일 존재 여부)
# CYCLE_STATE.txt는 이미 다음 사이클 번호를 가리키고 있음

# 3. 새 사이클 브리핑 생성
"$PY_BIN" scripts/cycle_dispatcher.py

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

# 5. Claude 세션이 커밋만 하고 push 못 한 경우 대비 — 마지막 안전망
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "cycle: 자동 개선 결과 (post-session sweep) $(date -u +'%Y-%m-%dT%H:%MZ')" || true
fi
# origin에 반영 (이미 push 됐으면 no-op)
if git rev-list --count @{u}..HEAD 2>/dev/null | grep -qv '^0$'; then
    echo "--- Pushing unpushed commits to origin/main ---"
    git push origin main || echo "git push failed — check auth/network"
else
    echo "origin/main 동기화 완료 (push 대상 없음)"
fi

echo "==================================="
echo "✅ Cycle completed: $(date -u +'%Y-%m-%d %H:%M:%SZ')"
echo "==================================="
