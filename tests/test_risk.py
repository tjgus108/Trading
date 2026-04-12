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


def test_total_exposure_blocked():
    """기존 포지션이 총 노출 한도(30%)를 초과하면 BLOCKED."""
    rm = RiskManager(max_total_exposure=0.30)
    # 계좌 10000, 기존 포지션: 3500 USD (35%) → 초과
    open_pos = [{"size": 0.07, "price": 50000}]  # 0.07 * 50000 = 3500
    result = rm.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        open_positions=open_pos,
    )
    assert result.status == RiskStatus.BLOCKED
    assert "total_exposure" in result.reason


def test_total_exposure_approved_under_limit():
    """기존 포지션이 총 노출 한도 미만이면 APPROVED."""
    rm = RiskManager(max_total_exposure=0.30)
    # 계좌 10000, 기존 포지션: 2000 USD (20%) → 통과
    open_pos = [{"size": 0.04, "price": 50000}]  # 0.04 * 50000 = 2000
    result = rm.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        open_positions=open_pos,
    )
    assert result.status == RiskStatus.APPROVED


# --- position_sizer config 의존성 테스트 ---
from src.risk.position_sizer import kelly_position_size, kelly_position_size_from_sizer

# config: risk_per_trade=0.01, max_position_size=0.1

def test_kelly_position_size_config_risk_per_trade():
    """config risk_per_trade(0.01)를 kelly_fraction으로 전달했을 때 결과가 양수이고 상한(25%) 이내."""
    capital = 10000.0
    result = kelly_position_size(
        win_rate=0.6,
        win_loss_ratio=2.0,
        capital=capital,
        kelly_fraction=0.01,  # config: risk_per_trade
    )
    assert result > 0, "포지션 금액은 양수여야 한다"
    assert result <= capital * 0.25, "내부 상한 25% 초과 불가"


def test_kelly_position_size_from_sizer_config_max_fraction():
    """config max_position_size(0.1)를 max_fraction으로 전달했을 때 수량이 상한 이내."""
    capital = 10000.0
    price = 50000.0
    max_fraction = 0.10  # config: max_position_size
    result = kelly_position_size_from_sizer(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=capital,
        price=price,
        kelly_fraction=0.25,
        max_fraction=max_fraction,
    )
    max_qty = (capital * max_fraction) / price
    assert result > 0, "수량은 양수여야 한다"
    assert result <= max_qty + 1e-9, f"max_fraction {max_fraction} 초과: {result} > {max_qty}"
