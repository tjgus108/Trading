"""H2. AdaptiveStrategySelector 테스트."""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock
from src.strategy.adaptive_selector import AdaptiveStrategySelector


def _make_strategy(name: str):
    s = MagicMock()
    s.name = name
    return s


def _make_selector():
    strats = {
        "ema_cross": _make_strategy("ema_cross"),
        "rsi_div": _make_strategy("rsi_div"),
        "funding": _make_strategy("funding"),
    }
    return AdaptiveStrategySelector(strats, window=20)


# ── 기본 동작 ──────────────────────────────────────────────────────────────

def test_record_and_sharpe_known():
    sel = _make_selector()
    # 양의 PnL 시리즈 기록
    for p in [10, 12, 8, 15, 9, 11, 13, 7, 10, 11]:
        sel.record_pnl("ema_cross", p)
    sh = sel.sharpe("ema_cross")
    assert sh > 0, "양의 PnL 시리즈 → 양의 Sharpe"


def test_sharpe_insufficient_data():
    sel = _make_selector()
    # 4개만 기록 (MIN_SAMPLES=5 미만)
    for p in [1, 2, 3, 4]:
        sel.record_pnl("ema_cross", p)
    assert sel.sharpe("ema_cross") == 0.0


def test_sharpe_unknown_strategy():
    sel = _make_selector()
    assert sel.sharpe("nonexistent") == 0.0


def test_record_unknown_strategy_no_error():
    sel = _make_selector()
    sel.record_pnl("nonexistent", 100.0)  # 에러 없이 무시


# ── 전략 선택 ────────────────────────────────────────────────────────────

def test_select_returns_strategy():
    sel = _make_selector()
    result = sel.select()
    assert result is not None


def test_select_fallback_uniform_no_history():
    sel = _make_selector()
    # 데이터 없을 때 균등 무작위 선택 — 여러 번 호출해도 에러 없음
    selected = set()
    for _ in range(50):
        s = sel.select()
        selected.add(s.name)
    # 3개 전략 중 적어도 1개는 선택되어야 함
    assert len(selected) >= 1


def test_select_prefers_best_strategy():
    sel = _make_selector()
    # ema_cross에 높은 Sharpe, rsi_div에 낮은 Sharpe
    for p in [20, 25, 22, 30, 18, 24, 26, 21, 23, 27]:
        sel.record_pnl("ema_cross", p)
    for p in [-1, -2, -1, 1, -1, 0, -2, 1, -1, 0]:
        sel.record_pnl("rsi_div", p)

    # 100회 선택 → ema_cross가 더 자주 선택되어야 함
    counts = {"ema_cross": 0, "rsi_div": 0, "funding": 0}
    for _ in range(100):
        s = sel.select()
        counts[s.name] += 1
    assert counts["ema_cross"] > counts["rsi_div"]


# ── best_strategy_name ────────────────────────────────────────────────────

def test_best_strategy_name():
    sel = _make_selector()
    for p in [10, 12, 11, 13, 9, 10, 11, 12, 10, 11]:
        sel.record_pnl("funding", p)
    assert sel.best_strategy_name() == "funding"


def test_best_strategy_no_history_returns_any():
    sel = _make_selector()
    name = sel.best_strategy_name()
    assert name in ["ema_cross", "rsi_div", "funding"]


# ── summary & add_strategy ────────────────────────────────────────────────

def test_summary_keys():
    sel = _make_selector()
    s = sel.summary()
    assert set(s.keys()) == {"ema_cross", "rsi_div", "funding"}
    assert all(isinstance(v, float) for v in s.values())


def test_add_strategy():
    sel = _make_selector()
    new_strat = _make_strategy("new_strat")
    sel.add_strategy("new_strat", new_strat)
    assert "new_strat" in sel.strategy_names()
    sel.record_pnl("new_strat", 5.0)  # 에러 없어야 함


# ── rolling_consistency ───────────────────────────────────────────────────

def test_rolling_consistency_all_positive():
    sel = _make_selector()
    for p in [5, 10, 8, 12, 6, 9, 11, 7, 10, 8]:
        sel.record_pnl("ema_cross", p)
    score = sel.rolling_consistency("ema_cross", window=30)
    assert score == 1.0, "모두 양수 → 일관성 1.0"


def test_rolling_consistency_mixed():
    sel = _make_selector()
    # 8 양수 + 2 음수 → dominant=8/10=0.8
    for p in [5, 10, -3, 8, 6, -1, 9, 7, 10, 8]:
        sel.record_pnl("ema_cross", p)
    score = sel.rolling_consistency("ema_cross", window=10)
    assert abs(score - 0.8) < 1e-9, f"expected 0.8, got {score}"


def test_rolling_consistency_insufficient_data():
    sel = _make_selector()
    for p in [1, 2, 3]:  # MIN_SAMPLES=5 미만
        sel.record_pnl("ema_cross", p)
    assert sel.rolling_consistency("ema_cross") == 0.0


def test_consistency_summary_keys():
    sel = _make_selector()
    result = sel.consistency_summary(window=30)
    assert set(result.keys()) == {"ema_cross", "rsi_div", "funding"}
    assert all(0.0 <= v <= 1.0 for v in result.values())


def test_select_single_strategy():
    """단일 전략일 때 select()가 항상 해당 전략을 반환."""
    strats = {"solo": _make_strategy("solo")}
    sel = AdaptiveStrategySelector(strats, window=10)
    result = sel.select()
    assert result.name == "solo"


def test_select_empty_history_all_negative_sharpe():
    """모든 Sharpe가 음수(데이터 부족)이면 균등 선택 — select() 에러 없음."""
    sel = _make_selector()
    # 4개만 기록 (MIN_SAMPLES 미달) → sharpe=0 → total=0 → 균등 선택
    sel.record_pnl("ema_cross", -5.0)
    sel.record_pnl("rsi_div", -5.0)
    result = sel.select()
    assert result is not None
    assert result.name in ["ema_cross", "rsi_div", "funding"]


def test_window_cap():
    """window=5 초과 기록 시 오래된 데이터 버림."""
    strats = {"a": _make_strategy("a")}
    sel = AdaptiveStrategySelector(strats, window=5)
    # 음수 10개 → 양수(다양한 값) 5개 순으로 기록
    for p in [-10, -10, -10, -10, -10]:
        sel.record_pnl("a", p)
    # 최신 5개는 서로 다른 양수 값 → std > 0 → Sharpe > 0
    for p in [8, 12, 9, 11, 10]:
        sel.record_pnl("a", p)
    # window=5이므로 최신 5개(양수)만 남아야 → Sharpe > 0
    sh = sel.sharpe("a")
    assert sh > 0, f"최신 양수 데이터만 남아야 하는데 Sharpe={sh}"


# ── 가중치 변동성 검증 ────────────────────────────────────────────────────

def test_weight_shifts_with_changing_sharpe():
    """PnL 패턴이 바뀌면 rolling Sharpe(가중치)가 실제로 변한다."""
    sel = _make_selector()
    # 초기: ema_cross 양호
    for p in [10, 12, 9, 11, 10, 13, 8, 11, 10, 12]:
        sel.record_pnl("ema_cross", p)
    # rsi_div: 혼합
    for p in [1, -2, 3, -1, 2, -3, 1, -2, 2, -1]:
        sel.record_pnl("rsi_div", p)
    sh_ema_before = sel.sharpe("ema_cross")
    sh_rsi_before = sel.sharpe("rsi_div")
    assert sh_ema_before > sh_rsi_before, "ema_cross Sharpe > rsi_div Sharpe"

    # 이후: rsi_div 성과 역전(양수 몰림)
    for p in [20, 22, 21, 25, 19, 23, 20, 22, 21, 24]:
        sel.record_pnl("rsi_div", p)
    sh_rsi_after = sel.sharpe("rsi_div")
    assert sh_rsi_after > sh_rsi_before, "새 데이터 반영 후 rsi_div Sharpe 상승"


def test_select_weight_proportional_after_reversal():
    """가중치 역전 후 select() 선택 빈도가 바뀐다."""
    sel = _make_selector()
    # ema_cross 초기 우세
    for p in [10, 12, 11, 13, 10, 12, 11, 13, 10, 12]:
        sel.record_pnl("ema_cross", p)
    # rsi_div 최신 10개 = 더 높은 Sharpe로 역전
    for p in [50, 55, 52, 58, 51, 53, 57, 54, 56, 55]:
        sel.record_pnl("rsi_div", p)

    counts = {"ema_cross": 0, "rsi_div": 0, "funding": 0}
    for _ in range(200):
        counts[sel.select().name] += 1
    assert counts["rsi_div"] > counts["ema_cross"], (
        f"rsi_div(high Sharpe) 선택 빈도가 더 높아야 함: {counts}"
    )
