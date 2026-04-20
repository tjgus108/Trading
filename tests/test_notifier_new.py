"""tests for notifier.py — Telegram API integration"""
import pytest
import os
from unittest.mock import patch, MagicMock
from src.exchange.notifier import Notifier, AlertLevel


def test_notifier_init_without_env():
    """Notifier initializes without Telegram env vars."""
    # Ensure env vars are not set
    with patch.dict(os.environ, {}, clear=True):
        notifier = Notifier(enabled=False)
        assert notifier.telegram_token is None
        assert notifier.telegram_chat_id is None
        assert notifier.telegram_enabled is False


def test_notifier_init_with_env():
    """Notifier initializes with Telegram env vars."""
    env = {
        "TELEGRAM_BOT_TOKEN": "test_token_123",
        "TELEGRAM_CHAT_ID": "test_chat_456",
    }
    with patch.dict(os.environ, env, clear=True):
        notifier = Notifier(enabled=True)
        assert notifier.telegram_token == "test_token_123"
        assert notifier.telegram_chat_id == "test_chat_456"
        assert notifier.telegram_enabled is True


def test_notifier_send_suppress():
    """SUPPRESS level does not queue or send."""
    notifier = Notifier(enabled=True)
    result = notifier.send("Test message", AlertLevel.SUPPRESS)
    assert result is False
    assert notifier.pending_count == 0


def test_notifier_send_silent_queues():
    """SILENT level queues message."""
    notifier = Notifier(enabled=True)
    result = notifier.send("Test silent message", AlertLevel.SILENT)
    assert result is True
    assert notifier.pending_count == 1


def test_notifier_send_critical_without_enabled():
    """CRITICAL without enabled=True does not send."""
    notifier = Notifier(enabled=False)
    result = notifier.send("Critical alert", AlertLevel.CRITICAL)
    assert result is False


def test_notifier_send_critical_with_enabled_but_no_env():
    """CRITICAL with enabled=True but no env vars does not deliver."""
    with patch.dict(os.environ, {}, clear=True):
        notifier = Notifier(enabled=True)
        result = notifier.send("Critical alert", AlertLevel.CRITICAL)
        # enabled=True but telegram_enabled=False, so _deliver returns False
        assert result is False


@patch('requests.post')
def test_notifier_deliver_success(mock_post):
    """_deliver sends message via Telegram API."""
    env = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHAT_ID": "test_chat",
    }
    mock_response = MagicMock()
    mock_response.ok = True
    mock_post.return_value = mock_response
    
    with patch.dict(os.environ, env, clear=True):
        notifier = Notifier(enabled=True)
        result = notifier._deliver("Test message")
        assert result is True
        mock_post.assert_called_once()


@patch('requests.post')
def test_notifier_deliver_failure(mock_post):
    """_deliver handles HTTP errors."""
    env = {
        "TELEGRAM_BOT_TOKEN": "test_token",
        "TELEGRAM_CHAT_ID": "test_chat",
    }
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_post.return_value = mock_response
    
    with patch.dict(os.environ, env, clear=True):
        notifier = Notifier(enabled=True)
        result = notifier._deliver("Test message")
        assert result is False


def test_notifier_flush_silent_empty():
    """flush_silent with no pending messages returns False."""
    notifier = Notifier(enabled=True)
    result = notifier.flush_silent()
    assert result is False


def test_notifier_flush_silent_with_messages():
    """flush_silent queues summary for delivery."""
    notifier = Notifier(enabled=False)
    notifier.send("Message 1", AlertLevel.SILENT)
    notifier.send("Message 2", AlertLevel.SILENT)
    assert notifier.pending_count == 2
    
    result = notifier.flush_silent()
    assert result is False  # enabled=False, so no delivery
    assert notifier.pending_count == 0  # Queue cleared


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
