"""RiskManager + CircuitBreaker 단위 테스트."""

import pytest
from src.risk.manager import CircuitBreaker, RiskManager, RiskStatus


@pytest.fixture
def risk_manager():
    cb = CircuitBreaker(max_daily_loss=0.05, max_drawdown=0.20)
    return RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        circuit_breaker=cb,
    )


def test_hold_always_approved(risk_manager):
    result = risk_manager.evaluate("HOLD", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size == 0


def test_buy_approved(risk_manager):
    result = risk_manager.evaluate("BUY", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0
    assert result.stop_loss < 50000
    assert result.take_profit > 50000


def test_sell_approved(risk_manager):
    result = risk_manager.evaluate("SELL", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.stop_loss > 50000
    assert result.take_profit < 50000


def test_circuit_breaker_flash_crash(risk_manager):
    result = risk_manager.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        last_candle_pct_change=-0.15,  # 15% 급락
    )
    assert result.status == RiskStatus.BLOCKED
    assert "flash crash" in result.reason


def test_circuit_breaker_drawdown():
    cb = CircuitBreaker(max_daily_loss=0.05, max_drawdown=0.10)
    rm = RiskManager(circuit_breaker=cb)
    # 피크 10000, 현재 8900 → 낙폭 11%
    cb._peak_balance = 10000
    result = rm.evaluate("BUY", entry_price=50000, atr=1000, account_balance=8900)
    assert result.status == RiskStatus.BLOCKED
    assert "drawdown" in result.reason


def test_position_size_max_cap():
    rm = RiskManager(max_position_size=0.05)  # 계좌의 5% 상한
    result = rm.evaluate("BUY", entry_price=50000, atr=100, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    max_size = (10000 * 0.05) / 50000
    assert result.position_size <= max_size + 1e-9


def test_risk_amount_equals_one_percent(risk_manager):
    result = risk_manager.evaluate("BUY", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert abs(result.risk_amount - 100.0) < 0.01  # 1% of 10000
