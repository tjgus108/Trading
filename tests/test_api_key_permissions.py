"""
ExchangeConnector.check_api_permissions() 단위 테스트.
실제 거래소 호출 없이 ccxt 객체를 mock한다.
"""

import logging
from unittest.mock import MagicMock, patch
import pytest

try:
    import ccxt
    HAS_CCXT = True
except ImportError:
    HAS_CCXT = False
    ccxt = None

from src.exchange.connector import ExchangeConnector


def _make_connector() -> ExchangeConnector:
    """_exchange를 mock으로 세팅한 커넥터를 반환한다."""
    conn = ExchangeConnector.__new__(ExchangeConnector)
    conn.exchange_name = "bybit"
    conn.sandbox = False
    conn._exchange = MagicMock()
    return conn


@pytest.mark.skipif(not HAS_CCXT, reason="ccxt not installed")
class TestCheckApiPermissions:
    def test_no_withdraw_logs_info(self, caplog):
        """출금 권한이 없으면 INFO 로그를 남기고 빈 withdraw=False를 반환한다."""
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.return_value = {
            "read": True,
            "trade": True,
            "withdraw": False,
        }

        with caplog.at_level(logging.INFO, logger="src.exchange.connector"):
            result = conn.check_api_permissions()

        assert result["withdraw"] is False
        assert any("permission check passed" in m for m in caplog.messages)

    def test_withdraw_enabled_logs_critical(self, caplog):
        """출금 권한이 있으면 CRITICAL 로그를 남긴다."""
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.return_value = {
            "read": True,
            "trade": True,
            "withdraw": True,
        }

        with caplog.at_level(logging.CRITICAL, logger="src.exchange.connector"):
            result = conn.check_api_permissions()

        assert result["withdraw"] is True
        critical_msgs = [
            m for m in caplog.messages if "WITHDRAW" in m or "SECURITY" in m
        ]
        assert critical_msgs, "Expected at least one CRITICAL log about WITHDRAW permission"

    def test_not_supported_returns_empty(self, caplog):
        """거래소가 fetchApiKeyPermissions를 지원하지 않으면 빈 dict를 반환하고 WARNING을 남긴다."""
        conn = _make_connector()
        conn._exchange.fetch_api_key_permissions.side_effect = ccxt.NotSupported("n/a")

        with caplog.at_level(logging.WARNING, logger="src.exchange.connector"):
            result = conn.check_api_permissions()

        assert result == {}
        assert any("does not support" in m for m in caplog.messages)

    def test_connect_calls_check_permissions(self):
        """connect() 완료 시 check_api_permissions()가 자동으로 호출된다."""
        conn = ExchangeConnector.__new__(ExchangeConnector)
        conn.exchange_name = "bybit"
        conn.sandbox = False
        conn._exchange = None

        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_api_key_permissions.return_value = {
            "withdraw": False
        }

        with patch("ccxt.bybit", return_value=mock_exchange_instance), \
             patch.dict("os.environ", {
                 "EXCHANGE_API_KEY": "test_key",
                 "EXCHANGE_API_SECRET": "test_secret",
             }):
            conn.connect()

        mock_exchange_instance.fetch_api_key_permissions.assert_called_once()
