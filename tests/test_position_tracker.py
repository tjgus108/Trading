"""PositionTracker + DailyPnL 단위 테스트."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.position_tracker import ClosedTrade, DailyPnL, Position, PositionTracker


def _pos(symbol="BTC/USDT", side="BUY", entry=50000.0, size=0.01, sl=49000.0, tp=53000.0):
    return Position(
        symbol=symbol,
        side=side,
        entry_price=entry,
        size=size,
        stop_loss=sl,
        take_profit=tp,
        opened_at=datetime.now(timezone.utc).isoformat(),
    )


# ── Position ──────────────────────────────────────────────────────────────

def test_unrealized_pnl_buy():
    pos = _pos(entry=50000, size=0.01)
    assert abs(pos.unrealized_pnl(51000) - 10.0) < 0.01   # +10 USDT


def test_unrealized_pnl_sell():
    pos = _pos(side="SELL", entry=50000, size=0.01)
    assert abs(pos.unrealized_pnl(49000) - 10.0) < 0.01   # +10 USDT


def test_position_to_md_row():
    pos = _pos()
    row = pos.to_md_row()
    assert "BTC/USDT" in row
    assert "BUY" in row
    assert "50000" in row


# ── DailyPnL ─────────────────────────────────────────────────────────────

def test_daily_pnl_accumulates():
    d = DailyPnL()
    d.record(100.0)
    d.record(-30.0)
    assert abs(d.realized - 70.0) < 0.01
    assert d.trade_count == 2
    assert d.wins == 1
    assert d.losses == 1


def test_daily_pnl_resets_on_new_day():
    d = DailyPnL()
    d.record(200.0)
    d.date = "2024-01-01"  # 날짜를 과거로 조작
    d.record(50.0)         # 새 날짜에 기록 → 리셋 후 50만 남음
    assert abs(d.realized - 50.0) < 0.01
    assert d.trade_count == 1


def test_daily_summary_format():
    d = DailyPnL()
    d.record(100.0)
    summary = d.summary()
    assert "Daily P&L" in summary
    assert "trades=1" in summary


# ── PositionTracker ───────────────────────────────────────────────────────

def test_open_and_has_position(tmp_path):
    tracker = PositionTracker()
    with patch("src.position_tracker.POSITIONS_FILE", str(tmp_path / "pos.md")):
        tracker.open_position(_pos())
        assert tracker.has_position("BTC/USDT")
        assert tracker.open_count() == 1


def test_close_position_calculates_pnl(tmp_path):
    tracker = PositionTracker()
    with patch("src.position_tracker.POSITIONS_FILE", str(tmp_path / "pos.md")):
        tracker.open_position(_pos(entry=50000, size=0.01))
        trade = tracker.close_position("BTC/USDT", exit_price=51000)

    assert trade is not None
    assert abs(trade.pnl - 10.0) < 0.01
    assert trade.reason == "MANUAL"
    assert not tracker.has_position("BTC/USDT")


def test_close_nonexistent_position_returns_none(tmp_path):
    tracker = PositionTracker()
    result = tracker.close_position("ETH/USDT", exit_price=3000)
    assert result is None


def test_close_sell_position_pnl(tmp_path):
    tracker = PositionTracker()
    with patch("src.position_tracker.POSITIONS_FILE", str(tmp_path / "pos.md")):
        tracker.open_position(_pos(side="SELL", entry=50000, size=0.01))
        trade = tracker.close_position("BTC/USDT", exit_price=49000)
    assert abs(trade.pnl - 10.0) < 0.01


def test_close_updates_daily_pnl(tmp_path):
    tracker = PositionTracker()
    with patch("src.position_tracker.POSITIONS_FILE", str(tmp_path / "pos.md")):
        tracker.open_position(_pos(entry=50000, size=0.01))
        tracker.close_position("BTC/USDT", exit_price=52000)
    assert abs(tracker.today_pnl() - 20.0) < 0.01


def test_close_calls_circuit_breaker(tmp_path):
    tracker = PositionTracker()
    cb = MagicMock()
    with patch("src.position_tracker.POSITIONS_FILE", str(tmp_path / "pos.md")):
        tracker.open_position(_pos(entry=50000, size=0.01))
        tracker.close_position("BTC/USDT", exit_price=49000, circuit_breaker=cb, account_balance=10000)
    cb.record_trade_result.assert_called_once()


def test_positions_file_written(tmp_path):
    pos_file = tmp_path / "POSITIONS.md"
    tracker = PositionTracker()
    with patch("src.position_tracker.POSITIONS_FILE", str(pos_file)):
        tracker.open_position(_pos())
    assert pos_file.exists()
    content = pos_file.read_text()
    assert "BTC/USDT" in content
    assert "Open Positions" in content
