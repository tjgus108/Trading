"""
ExchangeConnector.check_api_permissions 단위 테스트.
실제 거래소 호출 없이 ccxt mock으로 검증한다.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
import ccxt

from src.exchange.connector import ExchangeConnector


def _make_connector() -> ExchangeConnector:
    """연결된 것처럼 _exchange를 주입한 커넥터 반환."""
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    conn._exchange = MagicMock()
    return conn


def test_check_permissions_no_withdraw(caplog):
    """출금 권한 없음 → CRITICAL 없이 INFO 로그, dict 반환."""
    conn = _make_connector()
    conn._exchange.fetch_api_key_permissions.return_value = {
        "read": True,
        "trade": True,
        "withdraw": False,
    }

    with caplog.at_level(logging.INFO, logger="src.exchange.connector"):
        result = conn.check_api_permissions()

    assert result["withdraw"] is False
    assert result["trade"] is True
    # CRITICAL 로그가 없어야 한다
    critical_msgs = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert not critical_msgs, f"Unexpected CRITICAL log: {critical_msgs}"
    # INFO 통과 메시지 존재
    assert any("passed" in r.message for r in caplog.records)


def test_check_permissions_withdraw_enabled(caplog):
    """출금 권한 있음 → CRITICAL 경고 로그 발생."""
    conn = _make_connector()
    conn._exchange.fetch_api_key_permissions.return_value = {
        "read": True,
        "trade": True,
        "withdraw": True,
    }

    with caplog.at_level(logging.CRITICAL, logger="src.exchange.connector"):
        result = conn.check_api_permissions()

    assert result["withdraw"] is True
    critical_msgs = [r for r in caplog.records if r.levelno == logging.CRITICAL]
    assert critical_msgs, "Expected CRITICAL log when withdraw=True"
    assert "WITHDRAW" in critical_msgs[0].message


def test_check_permissions_not_supported(caplog):
    """fetchApiKeyPermissions 미지원 거래소 → 빈 dict 반환 + WARNING."""
    conn = _make_connector()
    conn._exchange.fetch_api_key_permissions.side_effect = ccxt.NotSupported("nope")

    with caplog.at_level(logging.WARNING, logger="src.exchange.connector"):
        result = conn.check_api_permissions()

    assert result == {}
    warn_msgs = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert warn_msgs, "Expected WARNING for unsupported exchange"


# ── MockExchangeConnector 경계 테스트 ──────────────────────────────────────

from src.exchange.mock_connector import MockExchangeConnector


def test_mock_buy_overdraft_clamps_to_zero():
    """buy 금액이 잔고를 초과해도 USDT 잔고가 음수가 되지 않는다."""
    conn = MockExchangeConnector(base_price=100.0)
    # 초기 USDT: 10000, 구매액: 100 * 200 = 20000 → max(0, ...) 로 0 이상이어야 함
    conn.create_order("BTC/USDT", "buy", 200.0)
    usdt = conn._balance["total"]["USDT"]
    assert usdt >= 0, f"USDT balance went negative: {usdt}"


def test_mock_sell_overdraft_clamps_to_zero():
    """sell 수량이 BTC 잔고를 초과해도 BTC 잔고가 음수가 되지 않는다."""
    conn = MockExchangeConnector(base_price=100.0)
    # 초기 BTC: 0.0, sell 1.0 → max(0, ...) 로 0 이상이어야 함
    conn.create_order("BTC/USDT", "sell", 1.0)
    btc = conn._balance["total"]["BTC"]
    assert btc >= 0, f"BTC balance went negative: {btc}"


# ── health_check 메서드 테스트 ─────────────────────────────────────────────

def test_health_check_not_connected():
    """미연결 상태 → health_check는 connected=False 반환."""
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    # _exchange 미설정 상태
    
    result = conn.health_check()
    
    assert result["connected"] is False
    assert result["exchange"] == "binance"
    assert result["sandbox"] is True
    assert result["markets_loaded"] is False
    assert result["last_tick"] is None


def test_health_check_connected():
    """연결된 상태 + 시장 로드됨 → connected=True, markets_loaded=True."""
    conn = _make_connector()
    conn._exchange.symbols = ["BTC/USDT", "ETH/USDT"]  # 시장이 로드됨
    
    result = conn.health_check()
    
    assert result["connected"] is True
    assert result["exchange"] == "binance"
    assert result["sandbox"] is True
    assert result["markets_loaded"] is True


def test_health_check_no_symbols():
    """연결 상태이나 시장 미로드 → markets_loaded=False."""
    conn = _make_connector()
    conn._exchange.symbols = []  # 시장 로드 안 됨
    
    result = conn.health_check()
    
    assert result["connected"] is True
    assert result["markets_loaded"] is False


def test_health_check_exception_handling():
    """연결 상태에서 예외 발생 → 안전하게 처리하고 connected=False."""
    conn = _make_connector()
    conn._exchange.symbols = None  # symbols가 없으면 예외 발생
    
    result = conn.health_check()
    
    assert result["connected"] is False
    assert result["exchange"] == "binance"


# ── create_order 재시도 테스트 ─────────────────────────────────────────────

def test_create_order_retries_on_network_error():
    """NetworkError 1회 후 성공 → 재시도 후 정상 반환."""
    conn = _make_connector()
    fake_order = {"id": "123", "status": "open"}
    conn._exchange.create_market_order.side_effect = [
        ccxt.NetworkError("timeout"),
        fake_order,
    ]

    result = conn.create_order("BTC/USDT", "buy", 0.01)

    assert result == fake_order
    assert conn._exchange.create_market_order.call_count == 2


def test_create_order_raises_after_max_retries():
    """NetworkError가 max_retries(2)번 계속되면 예외 전파."""
    conn = _make_connector()
    conn._exchange.create_market_order.side_effect = ccxt.NetworkError("persistent")

    with pytest.raises(ccxt.NetworkError):
        conn.create_order("BTC/USDT", "buy", 0.01, max_retries=2)

    assert conn._exchange.create_market_order.call_count == 2


# ── fetch_balance 견고성 테스트 ────────────────────────────────────────────

def test_fetch_balance_none_response(caplog):
    """fetch_balance가 None을 반환할 때 안전한 기본값을 돌려준다."""
    conn = _make_connector()
    conn._exchange.fetch_balance.return_value = None

    with caplog.at_level(logging.WARNING, logger="src.exchange.connector"):
        result = conn.fetch_balance()

    assert result == {"total": {}, "free": {}, "used": {}}
    assert any("unexpected" in r.message for r in caplog.records)


def test_fetch_balance_exception(caplog):
    """fetch_balance 호출 중 예외 발생 시 안전한 기본값을 돌려준다."""
    conn = _make_connector()
    conn._exchange.fetch_balance.side_effect = ccxt.NetworkError("connection dropped")

    with caplog.at_level(logging.WARNING, logger="src.exchange.connector"):
        result = conn.fetch_balance()

    assert result == {"total": {}, "free": {}, "used": {}}
    assert any("fetch_balance failed" in r.message for r in caplog.records)


# ── cancel_order 경계 테스트 ───────────────────────────────────────────────

def test_cancel_order_success():
    """정상 취소 → exchange.cancel_order 1회 호출, 결과 그대로 반환."""
    conn = _make_connector()
    fake_result = {"id": "ord-99", "status": "canceled", "symbol": "BTC/USDT"}
    conn._exchange.cancel_order.return_value = fake_result

    result = conn.cancel_order("ord-99", "BTC/USDT")

    conn._exchange.cancel_order.assert_called_once_with("ord-99", "BTC/USDT")
    assert result == fake_result


def test_cancel_order_not_connected():
    """미연결 상태에서 cancel_order 호출 → RuntimeError."""
    conn = ExchangeConnector(exchange_name="binance", sandbox=True)
    # _exchange 미설정

    with pytest.raises(RuntimeError, match="connect()"):
        conn.cancel_order("ord-99", "BTC/USDT")


# ── wait_for_fill 경계 테스트 ──────────────────────────────────────────────

def test_wait_for_fill_timeout_preserves_partial_fill():
    """timeout 발생 시 cancel 후 partial fill 수량(filled)을 반환에 포함."""
    conn = _make_connector()
    # fetch_order는 항상 open + partial fill 반환 (체결 안 됨)
    conn._exchange.fetch_order.return_value = {
        "id": "ord-1",
        "status": "open",
        "filled": 0.3,
        "amount": 1.0,
        "symbol": "BTC/USDT",
    }
    conn._exchange.cancel_order.return_value = {"id": "ord-1", "status": "canceled"}

    import unittest.mock as _mock
    # call1: deadline 설정(1000.0), call2: while 진입(1000.0 < 1001), call3: 탈출(2000.0)
    call_count = [0]
    def _time():
        call_count[0] += 1
        return 1000.0 if call_count[0] <= 2 else 2000.0

    with _mock.patch("src.exchange.connector.time.time", side_effect=_time), \
         _mock.patch("src.exchange.connector.time.sleep"):
        result = conn.wait_for_fill("ord-1", "BTC/USDT", timeout=1)

    assert result["status"] == "timeout"
    assert result["filled"] == 0.3, f"partial fill lost: {result}"
    assert result["amount"] == 1.0
    conn._exchange.cancel_order.assert_called_once()


def test_wait_for_fill_partial_fill_then_closed():
    """partial fill 후 최종 closed → closed 주문 그대로 반환."""
    conn = _make_connector()
    partial = {"id": "ord-2", "status": "open", "filled": 0.5, "amount": 1.0}
    filled = {"id": "ord-2", "status": "closed", "filled": 1.0, "amount": 1.0}
    conn._exchange.fetch_order.side_effect = [partial, filled]

    import unittest.mock as _mock
    # time은 항상 deadline 이내
    with _mock.patch("src.exchange.connector.time.time", return_value=500.0), \
         _mock.patch("src.exchange.connector.time.sleep"):
        result = conn.wait_for_fill("ord-2", "BTC/USDT", timeout=60)

    assert result["status"] == "closed"
    assert result["filled"] == 1.0
    conn._exchange.cancel_order.assert_not_called()
