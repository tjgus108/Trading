"""
lookahead_audit.py 단위 테스트.
"""
import sys
import os
import tempfile
from pathlib import Path

import pytest

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.lookahead_audit import audit_strategy, audit_all_strategies


# ── 헬퍼 ────────────────────────────────────────────────────────────────────

def _write_tmp(content: str, suffix: str = ".py") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    f.flush()
    f.close()
    return f.name


# ── audit_strategy 테스트 ────────────────────────────────────────────────────

def test_clean_file_returns_empty_risks():
    """깨끗한 파일은 risks=[] 반환."""
    code = "import pandas as pd\n\ndef generate(df):\n    last = df.iloc[-2]\n    return last['close']\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] == 0
    assert result["risks"] == []


def test_shift_negative_detected():
    """shift(-1) 포함 시 risk 탐지."""
    code = "df['future'] = df['close'].shift(-1)\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] >= 1
    assert any("shift" in r["description"] for r in result["risks"])


def test_shift_negative_line_number():
    """shift(-1)의 줄 번호가 정확히 반환되는지 확인."""
    code = "# header\nimport pandas as pd\ndf['x'] = df['close'].shift(-2)\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    risk_lines = [r["line"] for r in result["risks"]]
    assert 3 in risk_lines


def test_iloc_minus1_detected():
    """iloc[-1] 포함 시 risk 탐지."""
    code = "last_row = df.iloc[-1]\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] >= 1
    assert any("iloc[-1]" in r["description"] for r in result["risks"])


def test_tail1_detected():
    """.tail(1) 포함 시 risk 탐지."""
    code = "row = df.tail(1)\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] >= 1
    assert any("tail(1)" in r["description"] for r in result["risks"])


def test_rolling_without_shift_detected():
    """rolling().mean() 이후 shift 없이 사용 시 탐지."""
    code = "signal = df['close'].rolling(20).mean()\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] >= 1


def test_rolling_with_shift_not_flagged():
    """rolling().mean().shift(1)은 위험하지 않으므로 탐지 안 됨."""
    code = "signal = df['close'].rolling(20).mean().shift(1)\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    # rolling+shift 패턴은 안전 — risk_count가 0이어야 함
    rolling_risks = [r for r in result["risks"] if "rolling" in r["description"]]
    assert len(rolling_risks) == 0


def test_comment_line_ignored():
    """주석 줄의 패턴은 탐지하지 않음."""
    code = "# df['x'] = df.shift(-1)  # 이 줄은 주석\n"
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] == 0


def test_file_not_found_returns_error_key():
    """존재하지 않는 파일은 error 키 반환."""
    result = audit_strategy("/nonexistent/path/strategy.py")
    assert "error" in result
    assert result["risk_count"] == 0


def test_multiple_patterns_same_file():
    """여러 위험 패턴이 있는 파일에서 모두 탐지."""
    code = (
        "df['future'] = df['close'].shift(-3)\n"
        "last = df.iloc[-1]\n"
        "row = df.tail(1)\n"
    )
    path = _write_tmp(code)
    result = audit_strategy(path)
    assert result["risk_count"] >= 3


# ── audit_all_strategies 테스트 ─────────────────────────────────────────────

def test_audit_all_returns_list():
    """audit_all_strategies는 리스트를 반환."""
    tmpdir = tempfile.mkdtemp()
    # 파일 두 개 생성
    Path(tmpdir, "strat_a.py").write_text("x = 1\n")
    Path(tmpdir, "strat_b.py").write_text("df['f'] = df.shift(-1)\n")
    results = audit_all_strategies(tmpdir)
    assert isinstance(results, list)
    assert len(results) == 2


def test_audit_all_nonexistent_dir_returns_empty():
    """존재하지 않는 디렉토리는 빈 리스트 반환."""
    results = audit_all_strategies("/nonexistent/strategy_dir")
    assert results == []
