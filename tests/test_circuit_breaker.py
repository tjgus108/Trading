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
