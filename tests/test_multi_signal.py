"""I1. MultiStrategyAggregator 테스트 — 동적 가중치 포함."""

import sys
import os
import pytest
import pandas as pd
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.strategy.multi_signal import MultiStrategyAggregator
from src.strategy.base import Action, Confidence, Signal


# ── helpers ────────────────────────────────────────────────────────────────

def _df():
    """최소한의 두 행 DataFrame."""
    return pd.DataFrame({"close": [100.0, 101.0]})


def _make_strat(name: str, action: Action, conf: Confidence = Confidence.MEDIUM):
    strat = MagicMock()
    strat.name = name
    strat.generate.return_value = Signal(
        action=action, confidence=conf,
        strategy=name, entry_price=100.0,
        reasoning="test", invalidation="",
    )
    return strat


def _make_agg(*specs, perf_window=20, weights=None):
    """specs: list of (name, action, confidence)"""
    strats = [_make_strat(n, a, c) for n, a, c in specs]
    return MultiStrategyAggregator(strats, weights=weights, perf_window=perf_window)


# ── 기본 집계 동작 ─────────────────────────────────────────────────────────

def test_majority_buy():
    agg = _make_agg(
        ("a", Action.BUY, Confidence.HIGH),
        ("b", Action.BUY, Confidence.MEDIUM),
        ("c", Action.SELL, Confidence.LOW),
    )
    sig = agg.generate(_df())
    assert sig.action == Action.BUY


def test_majority_sell():
    agg = _make_agg(
        ("a", Action.SELL, Confidence.HIGH),
        ("b", Action.SELL, Confidence.MEDIUM),
        ("c", Action.BUY, Confidence.LOW),
    )
    sig = agg.generate(_df())
    assert sig.action == Action.SELL


def test_all_hold():
    agg = _make_agg(
        ("a", Action.HOLD, Confidence.MEDIUM),
        ("b", Action.HOLD, Confidence.HIGH),
    )
    sig = agg.generate(_df())
    assert sig.action == Action.HOLD


def test_no_strategies():
    agg = MultiStrategyAggregator([])
    sig = agg.generate(_df())
    assert sig.action == Action.HOLD


# ── perf_weight 기본 ────────────────────────────────────────────────────────

def test_perf_weight_no_data_is_one():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    assert agg._perf_weight("a") == 1.0


def test_perf_weight_insufficient_samples():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    for _ in range(4):  # MIN_PERF_SAMPLES=5 미만
        agg.record_outcome("a", 1)
    assert agg._perf_weight("a") == 1.0


def test_perf_weight_all_correct():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    for _ in range(5):
        agg.record_outcome("a", 1)
    # acc=1.0 → weight=2.0
    assert agg._perf_weight("a") == pytest.approx(2.0)


def test_perf_weight_all_wrong():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    for _ in range(5):
        agg.record_outcome("a", 0)
    # acc=0.0 → weight=0.5
    assert agg._perf_weight("a") == pytest.approx(0.5)


def test_perf_weight_half_correct():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    for _ in range(5):
        agg.record_outcome("a", 1)
    for _ in range(5):
        agg.record_outcome("a", 0)
    # acc=0.5 → weight=1.25
    assert agg._perf_weight("a") == pytest.approx(1.25)


# ── 동적 가중치가 집계에 반영되는지 ──────────────────────────────────────────

def test_dynamic_weight_boosts_accurate_strategy():
    """정확한 전략(a)의 BUY vs 부정확한 전략(b)의 SELL → BUY 승."""
    agg = _make_agg(
        ("a", Action.BUY, Confidence.MEDIUM),
        ("b", Action.SELL, Confidence.MEDIUM),
        perf_window=20,
    )
    # a: 높은 적중률
    for _ in range(10):
        agg.record_outcome("a", 1)
    # b: 낮은 적중률
    for _ in range(10):
        agg.record_outcome("b", 0)

    sig = agg.generate(_df())
    assert sig.action == Action.BUY


def test_dynamic_weight_suppresses_inaccurate_strategy():
    """부정확한 전략(a)의 BUY만 있을 때 perf_weight < 1 이 반영."""
    agg = _make_agg(("a", Action.BUY, Confidence.MEDIUM))
    for _ in range(10):
        agg.record_outcome("a", 0)  # 모두 오답
    # perf_weight=0.5 가 적용되어도 BUY 유일하면 BUY
    sig = agg.generate(_df())
    assert sig.action == Action.BUY


# ── record_outcome 경계 ─────────────────────────────────────────────────────

def test_record_unknown_strategy_no_error():
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH))
    agg.record_outcome("nonexistent", 1)  # 에러 없어야 함


def test_window_rolls_over():
    """perf_window=5 초과 시 오래된 데이터 버림."""
    agg = _make_agg(("a", Action.BUY, Confidence.HIGH), perf_window=5)
    for _ in range(5):
        agg.record_outcome("a", 0)  # 오래된 오답들
    for _ in range(5):
        agg.record_outcome("a", 1)  # 최신 정답들
    # 최신 5개만 남으므로 acc=1.0 → weight=2.0
    assert agg._perf_weight("a") == pytest.approx(2.0)


# ── performance_summary ─────────────────────────────────────────────────────

def test_performance_summary_keys():
    agg = _make_agg(
        ("a", Action.BUY, Confidence.HIGH),
        ("b", Action.SELL, Confidence.LOW),
    )
    summary = agg.performance_summary()
    assert set(summary.keys()) == {"a", "b"}
    for v in summary.values():
        assert "accuracy" in v and "samples" in v and "perf_weight" in v


def test_performance_summary_no_data():
    agg = _make_agg(("a", Action.HOLD, Confidence.MEDIUM))
    s = agg.performance_summary()["a"]
    assert s["accuracy"] is None
    assert s["samples"] == 0
    assert s["perf_weight"] == 1.0
