"""
RiskManager / CircuitBreaker 단위 테스트.
"""

import pytest
from src.risk.manager import CircuitBreaker, RiskManager, RiskStatus


# ── CircuitBreaker ────────────────────────────────────────────────────────────

def _make_cb(**kwargs) -> CircuitBreaker:
    defaults = dict(max_daily_loss=0.05, max_drawdown=0.10, max_consecutive_losses=3)
    defaults.update(kwargs)
    return CircuitBreaker(**defaults)


def test_circuit_breaker_no_trigger():
    cb = _make_cb()
    result = cb.check(current_balance=10000, last_candle_pct_change=0.01)
    assert result is None


def test_circuit_breaker_daily_loss_trigger():
    cb = _make_cb(max_daily_loss=0.05)
    cb._daily_loss = 0.06
    result = cb.check(current_balance=10000, last_candle_pct_change=0.0)
    assert result is not None
    assert "daily_loss" in result


def test_circuit_breaker_drawdown_trigger():
    cb = _make_cb(max_drawdown=0.10)
    cb._peak_balance = 10000
    result = cb.check(current_balance=8900, last_candle_pct_change=0.0)
    assert result is not None
    assert "drawdown" in result


def test_circuit_breaker_consecutive_losses_trigger():
    cb = _make_cb(max_consecutive_losses=3)
    cb._consecutive_losses = 3
    result = cb.check(current_balance=10000, last_candle_pct_change=0.0)
    assert result is not None
    assert "consecutive_losses" in result


def test_circuit_breaker_flash_crash_trigger():
    cb = _make_cb(flash_crash_pct=0.10)
    result = cb.check(current_balance=10000, last_candle_pct_change=-0.15)
    assert result is not None
    assert "flash crash" in result


def test_circuit_breaker_record_trade_result_loss():
    cb = _make_cb()
    cb.record_trade_result(pnl=-500, account_balance=10000)
    assert cb._daily_loss == pytest.approx(0.05)
    assert cb._consecutive_losses == 1


def test_circuit_breaker_record_trade_result_profit():
    cb = _make_cb()
    cb._consecutive_losses = 2
    cb.record_trade_result(pnl=200, account_balance=10000)
    assert cb._consecutive_losses == 0


def test_circuit_breaker_reset_daily():
    """reset_daily() 후 _daily_loss == 0, _consecutive_losses == 0"""
    cb = _make_cb()
    cb._daily_loss = 0.08
    cb._consecutive_losses = 3
    cb.reset_daily()
    assert cb._daily_loss == 0.0
    assert cb._consecutive_losses == 0


# ── RiskManager ───────────────────────────────────────────────────────────────

def _make_rm(**kwargs) -> RiskManager:
    return RiskManager(**kwargs)


def test_risk_manager_hold_approved():
    rm = _make_rm()
    result = rm.evaluate(action="HOLD", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size == 0


def test_risk_manager_buy_approved():
    rm = _make_rm(risk_per_trade=0.01, atr_multiplier_sl=1.5)
    result = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0
    assert result.stop_loss < 50000
    assert result.take_profit > 50000


def test_risk_manager_sell_approved():
    rm = _make_rm()
    result = rm.evaluate(action="SELL", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.stop_loss > 50000
    assert result.take_profit < 50000


def test_risk_manager_circuit_breaker_blocks():
    cb = _make_cb()
    cb._daily_loss = 0.10  # 한도 초과
    rm = _make_rm(circuit_breaker=cb)
    result = rm.evaluate(action="BUY", entry_price=50000, atr=500, account_balance=10000)
    assert result.status == RiskStatus.BLOCKED
    assert "Circuit breaker" in result.reason


def test_risk_manager_reset_daily_delegates():
    """RiskManager.reset_daily() → CircuitBreaker.reset_daily() 위임"""
    cb = _make_cb()
    cb._daily_loss = 0.09
    cb._consecutive_losses = 2
    rm = _make_rm(circuit_breaker=cb)
    rm.reset_daily()
    assert cb._daily_loss == 0.0
    assert cb._consecutive_losses == 0


def test_risk_manager_reset_daily_no_cb():
    """circuit_breaker 없을 때 reset_daily()가 예외 없이 실행"""
    rm = _make_rm(circuit_breaker=None)
    rm.reset_daily()  # 예외 없어야 함
