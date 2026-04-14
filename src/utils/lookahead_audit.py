"""
Lookahead Bias 감사 도구.
전략 코드에서 미래 데이터 유입 가능성을 검사.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict, Tuple


# (regex_pattern, description)
_RISK_PATTERNS: List[Tuple[str, str]] = [
    (r"shift\s*\(\s*-\d+", "shift(-N): 미래 데이터 참조 (lookahead bias)"),
    (r"\.iloc\s*\[\s*-1\s*\]", "iloc[-1]: 마지막 행 직접 접근 (미완성 캔들 위험)"),
    (r"\.tail\s*\(\s*1\s*\)", ".tail(1): 마지막 행 직접 접근 (미완성 캔들 위험)"),
    (
        r"\.rolling\s*\([^)]*\)\s*\.\s*(?:mean|sum|std|var|min|max)\s*\(\s*\)"
        r"(?!\s*\.\s*shift\s*\()",
        "rolling().mean() 등에 shift() 없이 즉시 사용 (윈도우 정렬 오류 가능)",
    ),
]


def audit_strategy(strategy_file: str) -> dict:
    """
    전략 파일을 읽어 위험 패턴 탐지.

    Returns:
        {
            "file": str,
            "risks": [{"line": int, "pattern": str, "description": str}],
            "risk_count": int,
        }
    """
    path = Path(strategy_file)
    if not path.exists():
        return {"file": strategy_file, "risks": [], "risk_count": 0, "error": "file not found"}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        return {"file": strategy_file, "risks": [], "risk_count": 0, "error": str(e)}

    risks: List[dict] = []
    for lineno, line in enumerate(lines, start=1):
        # 주석 줄은 건너뜀
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for pattern, description in _RISK_PATTERNS:
            if re.search(pattern, line):
                risks.append(
                    {
                        "line": lineno,
                        "pattern": pattern,
                        "description": description,
                    }
                )
                break  # 한 줄에 첫 번째 위험만 기록

    return {
        "file": str(path),
        "risks": risks,
        "risk_count": len(risks),
    }


def audit_all_strategies(strategy_dir: str = "src/strategy") -> List[dict]:
    """모든 전략 파일을 감사하고 위험 목록 반환."""
    base = Path(strategy_dir)
    if not base.exists():
        return []

    results: List[dict] = []
    for py_file in sorted(base.glob("**/*.py")):
        if py_file.name.startswith("__"):
            continue
        result = audit_strategy(str(py_file))
        results.append(result)
    return results
