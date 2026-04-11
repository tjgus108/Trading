"""
5시간 주기 작업 디스패처.
MASTER_PLAN.md의 로테이션 스케줄에 따라 3개 카테고리를 선택하고
각 카테고리를 Claude agent에게 병렬 배정한다.

사용법 (home laptop에서):
    # 수동 실행
    python3 scripts/cycle_dispatcher.py

    # cron 등록 (5시간마다)
    crontab -e
    0 */5 * * * cd ~/Trading && /usr/local/bin/python3 scripts/cycle_dispatcher.py >> /tmp/cycle.log 2>&1

    또는 Claude Code 세션 내에서:
    /loop 5h "scripts/cycle_dispatcher.py를 실행하고 결과대로 작업 진행"
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".claude-state"
CYCLE_FILE = STATE_DIR / "CYCLE_STATE.txt"
WORKLOG = STATE_DIR / "WORKLOG.md"
STATUS = ROOT / "STATUS.md"

# 로테이션 테이블 (MASTER_PLAN.md와 일치해야 함)
ROTATION = [
    # (cycle_num, [categories])
    (1, ["A", "C", "F"]),  # 품질 + 데이터 + 리서치
    (2, ["B", "D", "F"]),  # 리스크 + ML + 리서치
    (3, ["E", "A", "F"]),  # 실행 + 품질 + 리서치
    (4, ["C", "B", "F"]),  # 데이터 + 리스크 + 리서치
    (5, ["D", "E", "F"]),  # ML + 실행 + 리서치
]

CATEGORY_INFO = {
    "A": {
        "name": "Quality Assurance",
        "agent": "backtest-agent",
        "focus": "전략 품질 재검증, 테스트 커버리지, 기존 실패 테스트 수정",
    },
    "B": {
        "name": "Risk Management",
        "agent": "risk-agent",
        "focus": "DrawdownMonitor, Kelly Sizer 튜닝, CircuitBreaker 개선, VaR/CVaR 검증",
    },
    "C": {
        "name": "Data & Infrastructure",
        "agent": "data-agent",
        "focus": "WebSocket 안정성, DataFeed 캐시, OrderFlow 정확도, 온체인 데이터",
    },
    "D": {
        "name": "ML & Signals",
        "agent": "ml-agent",
        "focus": "LSTM 재학습, RF 피처 분석, 앙상블 가중치, Walk-Forward 통합",
    },
    "E": {
        "name": "Execution",
        "agent": "execution-agent",
        "focus": "Paper Trading, TWAP 검증, 슬리피지 모델, Telegram 알림",
    },
    "F": {
        "name": "Research",
        "agent": "strategy-researcher-agent",
        "focus": "트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)",
    },
}

FORBIDDEN = [
    "새 전략 파일 생성 금지 (현재 ~355개로 충분)",
    "한 카테고리에 2 사이클 연속 집중 금지",
    "실패 사례 리서치 없이 코드만 작성 금지",
]


def read_cycle() -> int:
    if CYCLE_FILE.exists():
        try:
            return int(CYCLE_FILE.read_text().strip())
        except ValueError:
            return 1
    return 1


def write_cycle(n: int) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    CYCLE_FILE.write_text(str(n))


def get_categories_for_cycle(cycle: int) -> list[str]:
    idx = (cycle - 1) % len(ROTATION)
    _, cats = ROTATION[idx]
    return cats



def read_worklog_summary() -> dict:
    """WORKLOG에서 마지막 COMPLETED 항목과 이슈 감지 정보를 반환."""
    if not WORKLOG.exists():
        return {"last_cycle": None, "issues": []}

    text = WORKLOG.read_text()

    # 마지막 COMPLETED 항목 추출
    completed = re.findall(
        r"## \[([^\]]+)\] (Cycle \d+ COMPLETED[^\n]*)\n(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    last_cycle_info = None
    if completed:
        ts, title, body = completed[-1]
        # body에서 첫 3줄 요약 (카테고리별 한 줄씩)
        summary_lines = [l for l in body.strip().splitlines() if l.strip()][:4]
        last_cycle_info = {"ts": ts, "title": title, "summary": summary_lines}

    # 이슈 감지: pending critical / FAIL / ERROR 키워드
    issues = []
    recent_lines = text.splitlines()[-200:]  # 최근 200줄만 검사
    issue_keywords = [
        ("CRITICAL", "CRITICAL 항목 감지"),
        ("FAIL", "FAIL 기록 존재"),
        ("ERROR", "ERROR 기록 존재"),
        ("pending", "pending 항목 존재"),
    ]
    seen = set()
    for keyword, label in issue_keywords:
        for line in recent_lines:
            if keyword in line and label not in seen:
                issues.append(label)
                seen.add(label)
                break

    return {"last_cycle": last_cycle_info, "issues": issues}


def build_briefing(cycle: int) -> str:
    cats = get_categories_for_cycle(cycle)
    lines = [
        "=" * 70,
        f"🔄 CYCLE {cycle} — {datetime.utcnow().isoformat()}Z",
        "=" * 70,
        "",
        "## 이번 사이클 배정 카테고리 (병렬 3개)",
        "",
    ]
    for cat_code in cats:
        info = CATEGORY_INFO[cat_code]
        lines.append(f"### [{cat_code}] {info['name']}")
        lines.append(f"- **Agent**: {info['agent']}")
        lines.append(f"- **Focus**: {info['focus']}")
        lines.append("")

    # WORKLOG 최근 현황 삽입
    wl = read_worklog_summary()
    lines.append("## 이전 사이클 현황")
    if wl["last_cycle"]:
        lc = wl["last_cycle"]
        lines.append(f"**{lc['title']}** ({lc['ts']})")
        for sl in lc["summary"]:
            lines.append(f"  {sl}")
    else:
        lines.append("  (기록 없음)")
    if wl["issues"]:
        lines.append("")
        lines.append("**[!] 감지된 이슈:**")
        for issue in wl["issues"]:
            lines.append(f"  - {issue}")
    lines.append("")

    lines.append("## ⛔ 금지 사항")
    for f in FORBIDDEN:
        lines.append(f"- {f}")
    lines.append("")

    lines.append("## 📋 사이클 종료 시 필수 수행")
    lines.append("1. .claude-state/WORKLOG.md 업데이트 (이번 사이클 작업 기록)")
    lines.append("2. STATUS.md 업데이트 (전체 현황)")
    lines.append("3. .claude-state/NEXT_STEPS.md 업데이트 (다음 작업 힌트)")
    lines.append("4. git add -A && git commit -m '[Cycle N] 카테고리 요약' && git push")
    lines.append("5. CYCLE_STATE.txt 다음 사이클 번호로 업데이트")
    lines.append("")

    lines.append("## 🚀 실행 지침 (Claude Code 세션용)")
    lines.append("이 브리핑을 읽은 Claude Code는 다음과 같이 진행:")
    lines.append("1. 위 3개 카테고리를 Agent tool로 *병렬* 실행")
    lines.append("2. 각 agent는 해당 카테고리 focus 항목 중 1~2개 실제 개선 작업 수행")
    lines.append("3. 모든 agent 완료 후 WORKLOG/STATUS/NEXT_STEPS 업데이트")
    lines.append("4. 커밋 + push")
    lines.append("")

    return "\n".join(lines)


def append_worklog(cycle: int, briefing_summary: str) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    if WORKLOG.exists():
        existing = WORKLOG.read_text()
    else:
        existing = "# Work Log\n"
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    cats = " + ".join(get_categories_for_cycle(cycle))
    entry = f"\n## [{ts}] Cycle {cycle} Dispatched — {cats}\n{briefing_summary}\n"
    WORKLOG.write_text(existing + entry)


def main() -> int:
    cycle = read_cycle()
    briefing = build_briefing(cycle)
    print(briefing)

    # 브리핑을 파일로 저장 (Claude Code 세션이 읽도록)
    briefing_path = STATE_DIR / "CURRENT_CYCLE_BRIEFING.md"
    briefing_path.write_text(briefing)

    # 워크로그에 사이클 시작 기록
    cats = " + ".join(get_categories_for_cycle(cycle))
    append_worklog(cycle, f"Categories: {cats}. Briefing: {briefing_path.name}")

    # 다음 사이클 번호 저장
    write_cycle(cycle + 1)
    print(f"\n다음 실행 시 사이클 번호: {cycle + 1}")
    print(f"브리핑 파일: {briefing_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
