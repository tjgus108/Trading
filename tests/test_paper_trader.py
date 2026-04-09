"""tests/test_paper_trader.py — PaperTrader 단위 테스트"""
import pytest
from src.exchange.paper_trader import PaperTrader, PaperAccount, PaperTrade


# ── 기본 생성 ──────────────────────────────────────────────
def test_default_initial_balance():
    pt = PaperTrader()
    assert pt.account.initial_balance == 10000.0
    assert pt.account.balance == 10000.0


def test_custom_initial_balance():
    pt = PaperTrader(initial_balance=5000.0)
    assert pt.account.initial_balance == 5000.0
    assert pt.account.balance == 5000.0


def test_no_positions_on_init():
    pt = PaperTrader()
    assert pt.account.positions == {}
    assert pt.account.trades == []


# ── BUY 신호 ──────────────────────────────────────────────
def test_buy_reduces_balance():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.001)
    result = pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                               strategy="test", confidence="HIGH")
    assert result["status"] == "filled"
    expected_cost = 1000.0 * 1.0 * (1 + 0.001)  # price * qty * (1 + fee)
    assert abs(pt.account.balance - (10000.0 - expected_cost)) < 1e-6


def test_buy_creates_position():
    pt = PaperTrader()
    pt.execute_signal("BTC/USDT", "BUY", price=500.0, quantity=2.0,
                      strategy="test", confidence="LOW")
    assert pt.account.positions.get("BTC/USDT") == 2.0


def test_buy_records_trade():
    pt = PaperTrader()
    pt.execute_signal("ETH/USDT", "BUY", price=200.0, quantity=3.0,
                      strategy="rsi", confidence="MED")
    assert len(pt.account.trades) == 1
    t = pt.account.trades[0]
    assert t.symbol == "ETH/USDT"
    assert t.action == "BUY"


def test_buy_insufficient_balance_rejected():
    pt = PaperTrader(initial_balance=100.0)
    result = pt.execute_signal("BTC/USDT", "BUY", price=5000.0, quantity=1.0,
                               strategy="test", confidence="HIGH")
    assert result["status"] == "rejected"
    assert pt.account.balance == 100.0  # 변화 없음


def test_buy_accumulates_avg_entry():
    pt = PaperTrader(initial_balance=50000.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "BUY", price=2000.0, quantity=1.0,
                      strategy="s", confidence="H")
    avg = pt.account.avg_entry["BTC/USDT"]
    assert abs(avg - 1500.0) < 1e-6
    assert pt.account.positions["BTC/USDT"] == 2.0


# ── SELL 신호 ─────────────────────────────────────────────
def test_sell_calculates_pnl():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0)  # fee=0 for clean math
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    result = pt.execute_signal("BTC/USDT", "SELL", price=1200.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "filled"
    assert abs(result["pnl"] - 200.0) < 1e-6


def test_sell_increases_balance():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    balance_after_buy = pt.account.balance
    pt.execute_signal("BTC/USDT", "SELL", price=1200.0, quantity=1.0,
                      strategy="s", confidence="H")
    assert pt.account.balance > balance_after_buy


def test_sell_no_position_rejected():
    pt = PaperTrader()
    result = pt.execute_signal("BTC/USDT", "SELL", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "rejected"


def test_sell_removes_position():
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                      strategy="s", confidence="H")
    assert "BTC/USDT" not in pt.account.positions


# ── get_summary ───────────────────────────────────────────
def test_summary_keys():
    pt = PaperTrader()
    summary = pt.get_summary()
    for key in ("initial_balance", "current_balance", "total_pnl",
                "total_return_pct", "trade_count", "win_rate", "open_positions"):
        assert key in summary


def test_summary_total_return_positive_after_profit():
    pt = PaperTrader(initial_balance=10000.0, fee_rate=0.0)
    pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                      strategy="s", confidence="H")
    pt.execute_signal("BTC/USDT", "SELL", price=2000.0, quantity=1.0,
                      strategy="s", confidence="H")
    summary = pt.get_summary()
    assert summary["total_return_pct"] > 0


def test_summary_win_rate_all_wins():
    pt = PaperTrader(initial_balance=50000.0, fee_rate=0.0)
    for _ in range(3):
        pt.execute_signal("BTC/USDT", "BUY", price=1000.0, quantity=1.0,
                          strategy="s", confidence="H")
        pt.execute_signal("BTC/USDT", "SELL", price=1100.0, quantity=1.0,
                          strategy="s", confidence="H")
    summary = pt.get_summary()
    assert summary["win_rate"] == 1.0


def test_unknown_action_returns_error():
    pt = PaperTrader()
    result = pt.execute_signal("BTC/USDT", "HOLD", price=1000.0, quantity=1.0,
                               strategy="s", confidence="H")
    assert result["status"] == "error"
