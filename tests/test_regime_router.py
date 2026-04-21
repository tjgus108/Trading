"""
RegimeStrategyRouter 단위 테스트.
"""

import pytest
from src.strategy.regime_router import RegimeStrategyRouter, DEFAULT_STRATEGY_MAP


@pytest.fixture
def router():
    return RegimeStrategyRouter()


# ── 1. get_active_strategies ──────────────────────────────────────────────────

def test_trend_returns_trend_strategies(router):
    active = router.get_active_strategies("TREND")
    assert "cmf" in active
    assert "elder_impulse" in active
    # RANGE 전략 포함 안됨
    assert "wick_reversal" not in active
    assert "price_cluster" not in active


def test_range_returns_range_strategies(router):
    active = router.get_active_strategies("RANGE")
    assert "wick_reversal" in active
    assert "engulfing_zone" in active
    # TREND 전략 포함 안됨
    assert "cmf" not in active
    assert "momentum_quality" not in active


def test_crisis_returns_all_strategies(router):
    """CRISIS 명시 목록 없으면 TREND+RANGE 전체 반환."""
    active = router.get_active_strategies("CRISIS")
    # 양쪽 전략 모두 포함되어야 함
    assert "cmf" in active
    assert "wick_reversal" in active


def test_unknown_regime_returns_empty(router):
    active = router.get_active_strategies("SIDEWAYS")
    assert active == []


def test_lowercase_regime_works(router):
    active = router.get_active_strategies("trend")
    assert "cmf" in active


# ── 2. scale_position ─────────────────────────────────────────────────────────

def test_trend_scale_is_1x(router):
    assert router.scale_position("TREND", 100.0) == pytest.approx(100.0)


def test_range_scale_is_1x(router):
    assert router.scale_position("RANGE", 200.0) == pytest.approx(200.0)


def test_crisis_scale_is_half(router):
    result = router.scale_position("CRISIS", 100.0)
    assert result == pytest.approx(50.0)


def test_crisis_scale_lowercase(router):
    result = router.scale_position("crisis", 80.0)
    assert result == pytest.approx(40.0)


def test_unknown_regime_scale_defaults_to_1x(router):
    assert router.scale_position("UNKNOWN", 50.0) == pytest.approx(50.0)


# ── 3. should_skip ────────────────────────────────────────────────────────────

def test_skip_range_strategy_in_trend(router):
    assert router.should_skip("wick_reversal", "TREND") is True
    assert router.should_skip("price_cluster", "TREND") is True


def test_no_skip_trend_strategy_in_trend(router):
    assert router.should_skip("cmf", "TREND") is False
    assert router.should_skip("elder_impulse", "TREND") is False


def test_skip_trend_strategy_in_range(router):
    assert router.should_skip("cmf", "RANGE") is True
    assert router.should_skip("momentum_quality", "RANGE") is True


def test_no_skip_range_strategy_in_range(router):
    assert router.should_skip("wick_reversal", "RANGE") is False


def test_no_skip_in_crisis(router):
    """CRISIS 레짐에서는 전략을 스킵하지 않음 — 크기 감소로 처리."""
    assert router.should_skip("cmf", "CRISIS") is False
    assert router.should_skip("wick_reversal", "CRISIS") is False


def test_skip_unknown_regime(router):
    assert router.should_skip("cmf", "UNKNOWN_REGIME") is True


# ── 4. 레짐 전환 시나리오 ──────────────────────────────────────────────────────

def test_regime_switch_trend_to_range(router):
    """TREND → RANGE 전환 시 활성 전략 세트가 바뀌어야 함."""
    trend_active = set(router.get_active_strategies("TREND"))
    range_active = set(router.get_active_strategies("RANGE"))
    # 두 세트는 겹치지 않아야 함 (명시 전략 기준)
    assert trend_active.isdisjoint(range_active)


def test_regime_switch_to_crisis_reduces_position(router):
    base = 1000.0
    normal = router.scale_position("TREND", base)
    crisis = router.scale_position("CRISIS", base)
    assert crisis < normal
    assert crisis == pytest.approx(base * 0.5)


# ── 5. 커스텀 strategy_map ────────────────────────────────────────────────────

def test_custom_map_overrides_default():
    custom_map = {
        "TREND": ["strat_a", "strat_b"],
        "RANGE": ["strat_c"],
        "CRISIS": [],
    }
    r = RegimeStrategyRouter(strategy_map=custom_map)
    assert r.get_active_strategies("TREND") == ["strat_a", "strat_b"]
    assert r.should_skip("strat_c", "TREND") is True
    assert r.should_skip("strat_a", "RANGE") is True


def test_crisis_with_explicit_strategies():
    custom_map = {
        "TREND": ["strat_a"],
        "RANGE": ["strat_b"],
        "CRISIS": ["strat_c"],
    }
    r = RegimeStrategyRouter(strategy_map=custom_map)
    assert r.get_active_strategies("CRISIS") == ["strat_c"]
