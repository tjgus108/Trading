"""TradeLogger CSV 기록 단위 테스트."""

import csv
from pathlib import Path

from src.utils.trade_logger import TradeLogger


def test_trade_logger_writes_header_on_new_file(tmp_path: Path):
    csv_path = tmp_path / "trades.csv"
    TradeLogger(csv_path)
    with csv_path.open() as f:
        header = next(csv.reader(f))
    assert "timestamp_utc" in header
    assert "order_id" in header
    assert "fee" in header
    assert "strategy" in header


def test_trade_logger_log_fill_records_row(tmp_path: Path):
    csv_path = tmp_path / "trades.csv"
    tl = TradeLogger(csv_path)
    tl.log_fill(
        order={
            "id": "ord123",
            "clientOrderId": "bot_abc",
            "average": 50000.0,
            "filled": 0.01,
            "cost": 500.0,
            "fee": {"cost": 0.25, "currency": "USDT"},
            "status": "closed",
        },
        symbol="BTC/USDT",
        side="buy",
        strategy="bb_squeeze",
        note="entry",
    )
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    r = rows[0]
    assert r["order_id"] == "ord123"
    assert r["client_order_id"] == "bot_abc"
    assert r["price"] == "50000.0"
    assert r["amount"] == "0.01"
    assert r["fee"] == "0.25"
    assert r["fee_currency"] == "USDT"
    assert r["strategy"] == "bb_squeeze"
    assert r["note"] == "entry"


def test_trade_logger_handles_malformed_order_without_raising(tmp_path: Path):
    csv_path = tmp_path / "trades.csv"
    tl = TradeLogger(csv_path)
    # 예외 없이 흡수되고 row가 기록되어야 함
    tl.log_fill(order={}, symbol="BTC/USDT", side="sell")
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["side"] == "sell"


def test_trade_logger_appends_existing_file(tmp_path: Path):
    csv_path = tmp_path / "trades.csv"
    tl1 = TradeLogger(csv_path)
    tl1.log_fill(order={"id": "a"}, symbol="BTC/USDT", side="buy")
    # 새 인스턴스로 열어도 헤더 중복 없이 append
    tl2 = TradeLogger(csv_path)
    tl2.log_fill(order={"id": "b"}, symbol="BTC/USDT", side="sell")
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    assert [r["order_id"] for r in rows] == ["a", "b"]
