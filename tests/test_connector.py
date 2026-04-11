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
