"""tests/test_circuit_breaker.py — CircuitBreaker 단위 테스트"""
import pytest
from src.risk.circuit_breaker import CircuitBreaker


# ── 기본 생성 ──────────────────────────────────────────────
def test_default_limits():
    cb = CircuitBreaker()
    assert cb.daily_drawdown_limit == 0.05
    assert cb.total_drawdown_limit == 0.15


def test_not_triggered_on_init():
    cb = CircuitBreaker()
    assert cb.is_triggered is False


# ── 정상 범위 ──────────────────────────────────────────────
def test_no_trigger_within_limits():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9800.0,   # -2% daily
        peak_balance=10000.0,     # -2% total
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False
    assert result["reason"] == ""


# ── 일일 낙폭 트리거 ───────────────────────────────────────
def test_daily_drawdown_triggers_at_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9500.0,   # exactly -5% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is True
    assert "일일" in result["reason"]


def test_daily_drawdown_triggers_above_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=9400.0,   # -6% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is True
    assert result["drawdown_pct"] > 0.05


# ── 전체 낙폭 트리거 ───────────────────────────────────────
def test_total_drawdown_triggers_at_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    # daily_start=8600: daily dd = (8600-8500)/8600 ≈ 1.16% < 5%, total dd = 15%
    result = cb.check(
        current_balance=8500.0,
        peak_balance=10000.0,
        daily_start_balance=8600.0,
    )
    assert result["triggered"] is True
    assert "전체" in result["reason"]


def test_total_drawdown_triggers_above_limit():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    result = cb.check(
        current_balance=8000.0,   # -20% total
        peak_balance=10000.0,
        daily_start_balance=9800.0,
    )
    assert result["triggered"] is True


# ── reset_daily ────────────────────────────────────────────
def test_reset_daily_clears_daily_trigger():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    cb.check(current_balance=9400.0, peak_balance=10000.0, daily_start_balance=10000.0)
    assert cb.is_triggered is True
    cb.reset_daily(daily_start_balance=9400.0)
    assert cb.is_triggered is False


def test_reset_daily_keeps_total_trigger():
    cb = CircuitBreaker(daily_drawdown_limit=0.05, total_drawdown_limit=0.15)
    # total 낙폭으로만 트리거: daily_start=8500 → daily dd=(8500-8400)/8500≈1.2%<5%
    cb.check(current_balance=8400.0, peak_balance=10000.0, daily_start_balance=8500.0)
    assert cb.is_triggered is True
    assert "전체" in cb._reason
    cb.reset_daily(daily_start_balance=8400.0)
    # 전체 낙폭 트리거는 유지
    assert cb.is_triggered is True


def test_reset_all_clears_everything():
    cb = CircuitBreaker()
    cb.check(current_balance=8000.0, peak_balance=10000.0, daily_start_balance=10000.0)
    cb.reset_all()
    assert cb.is_triggered is False
    result = cb.check(current_balance=9800.0, peak_balance=10000.0, daily_start_balance=10000.0)
    assert result["triggered"] is False


# ── 변동성 급등 (ATR surge) ────────────────────────────────
def test_atr_surge_returns_half_size_multiplier():
    """ATR이 기준의 2배 이상 → triggered=False, size_multiplier=0.5, volatility_surge=True"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.04,   # 4% — 기준 2%의 2배
        baseline_atr=0.02,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is True
    assert result["size_multiplier"] == 0.5
    assert "ATR 급등" in result["reason"]


def test_atr_below_surge_threshold_no_effect():
    """ATR이 기준의 1.9배 → 급등 아님, 정상 통과"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.038,   # 1.9배 < 2.0
        baseline_atr=0.02,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is False
    assert result["size_multiplier"] == 1.0


def test_atr_surge_does_not_override_drawdown_trigger():
    """낙폭 조건 먼저 트리거되면 ATR surge는 무관 — triggered=True, size_multiplier=0.0"""
    cb = CircuitBreaker(daily_drawdown_limit=0.05, atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9400.0,   # -6% daily
        peak_balance=10000.0,
        daily_start_balance=10000.0,
        current_atr=0.10,
        baseline_atr=0.02,
    )
    assert result["triggered"] is True
    assert result["size_multiplier"] == 0.0
    assert "일일" in result["reason"]


def test_atr_surge_without_atr_args_no_effect():
    """current_atr/baseline_atr 미전달 시 ATR 체크 스킵"""
    cb = CircuitBreaker(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=9900.0,
        peak_balance=10000.0,
        daily_start_balance=10000.0,
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is False
    assert result["size_multiplier"] == 1.0
