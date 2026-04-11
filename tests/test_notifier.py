"""
Tests for TelegramNotifier.
No real Telegram or exchange connection required.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.notifier import TelegramNotifier, _format_pipeline
from src.pipeline.runner import PipelineResult
from src.strategy.base import Action, Confidence, Signal
from src.risk.manager import RiskResult, RiskStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pipeline_result(**overrides) -> PipelineResult:
    defaults = dict(
        timestamp="2026-04-07 12:00 UTC",
        symbol="BTC/USDT",
        pipeline_step="execution",
        status="OK",
    )
    defaults.update(overrides)
    return PipelineResult(**defaults)


def _make_signal(action=Action.BUY) -> Signal:
    return Signal(
        action=action,
        confidence=Confidence.HIGH,
        strategy="test",
        entry_price=65000.0,
        reasoning="test reasoning",
        invalidation="test invalidation",
    )


def _make_risk(status=RiskStatus.APPROVED) -> RiskResult:
    return RiskResult(
        status=status,
        reason=None,
        position_size=0.0012,
        stop_loss=63000.0,
        take_profit=68000.0,
        risk_amount=78.0,
        portfolio_exposure=0.05,
    )


# ---------------------------------------------------------------------------
# Silent skip when no token
# ---------------------------------------------------------------------------

class TestNoToken:
    def test_notify_pipeline_skips_without_token(self):
        notifier = TelegramNotifier(bot_token="", chat_id="")
        result = _make_pipeline_result()
        # Should not raise and should not call requests.post
        with patch("src.notifier.requests.post") as mock_post:
            notifier.notify_pipeline(result)
            mock_post.assert_not_called()

    def test_notify_error_skips_without_token(self):
        notifier = TelegramNotifier(bot_token="", chat_id="")
        with patch("src.notifier.requests.post") as mock_post:
            notifier.notify_error("something went wrong")
            mock_post.assert_not_called()

    def test_notify_startup_skips_without_token(self):
        notifier = TelegramNotifier(bot_token="", chat_id="")
        with patch("src.notifier.requests.post") as mock_post:
            notifier.notify_startup("donchian_breakout", "BTC/USDT", dry_run=True)
            mock_post.assert_not_called()

    def test_enabled_false_skips_even_with_token(self):
        notifier = TelegramNotifier(bot_token="tok", chat_id="123", enabled=False)
        with patch("src.notifier.requests.post") as mock_post:
            notifier.notify_pipeline(_make_pipeline_result())
            mock_post.assert_not_called()

    def test_reads_token_from_env(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "envtoken")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "envchatid")
        notifier = TelegramNotifier()
        assert notifier._token == "envtoken"
        assert notifier._chat_id == "envchatid"
        assert notifier._enabled is True

    def test_missing_env_stays_disabled(self, monkeypatch):
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
        notifier = TelegramNotifier()
        assert notifier._enabled is False


# ---------------------------------------------------------------------------
# Message format
# ---------------------------------------------------------------------------

class TestMessageFormat:
    def test_pipeline_basic_fields(self):
        result = _make_pipeline_result()
        msg = _format_pipeline(result)
        assert "BTC/USDT" in msg
        assert "execution" in msg
        assert "OK" in msg
        assert "2026-04-07 12:00 UTC" in msg

    def test_pipeline_with_signal(self):
        result = _make_pipeline_result(signal=_make_signal())
        msg = _format_pipeline(result)
        assert "BUY" in msg
        assert "65,000.00" in msg
        assert "HIGH" in msg

    def test_pipeline_with_risk_approved(self):
        result = _make_pipeline_result(signal=_make_signal(), risk=_make_risk())
        msg = _format_pipeline(result)
        assert "APPROVED" in msg
        assert "0.0012" in msg

    def test_pipeline_with_risk_blocked(self):
        risk = _make_risk(status=RiskStatus.BLOCKED)
        risk.reason = "max drawdown exceeded"
        result = _make_pipeline_result(signal=_make_signal(), risk=risk, status="BLOCKED")
        msg = _format_pipeline(result)
        assert "BLOCKED" in msg
        assert "max drawdown exceeded" in msg

    def test_pipeline_with_error(self):
        result = _make_pipeline_result(status="ERROR", error="connection timeout")
        msg = _format_pipeline(result)
        assert "ERROR" in msg
        assert "connection timeout" in msg

    def test_pipeline_with_notes(self):
        result = _make_pipeline_result(notes=["dry_run=True — order not submitted"])
        msg = _format_pipeline(result)
        assert "dry_run=True" in msg

    def test_no_emojis_in_pipeline_message(self):
        result = _make_pipeline_result(signal=_make_signal(), risk=_make_risk())
        msg = _format_pipeline(result)
        # Verify no common emoji characters appear
        for char in ["🚀", "✅", "❌", "⚠️", "📊", "💰"]:
            assert char not in msg

    def test_startup_message_contains_key_fields(self):
        notifier = TelegramNotifier(bot_token="tok", chat_id="123")
        captured = []

        with patch.object(notifier, "_send", side_effect=captured.append):
            notifier.notify_startup("donchian_breakout", "BTC/USDT", dry_run=True)

        assert len(captured) == 1
        msg = captured[0]
        assert "donchian_breakout" in msg
        assert "BTC/USDT" in msg
        assert "DRY RUN" in msg

    def test_startup_live_mode_label(self):
        notifier = TelegramNotifier(bot_token="tok", chat_id="123")
        captured = []

        with patch.object(notifier, "_send", side_effect=captured.append):
            notifier.notify_startup("ema_cross", "ETH/USDT", dry_run=False)

        assert "LIVE" in captured[0]

    def test_error_message_format(self):
        notifier = TelegramNotifier(bot_token="tok", chat_id="123")
        captured = []

        with patch.object(notifier, "_send", side_effect=captured.append):
            notifier.notify_error("exchange unreachable")

        assert "[ERROR]" in captured[0]
        assert "exchange unreachable" in captured[0]


# ---------------------------------------------------------------------------
# HTTP send behavior
# ---------------------------------------------------------------------------

class TestSendBehavior:
    def _notifier(self) -> TelegramNotifier:
        return TelegramNotifier(bot_token="testtoken", chat_id="987654")

    def test_send_posts_to_correct_url(self):
        notifier = self._notifier()
        mock_resp = MagicMock()
        mock_resp.ok = True

        with patch("src.notifier.requests.post", return_value=mock_resp) as mock_post:
            notifier._send("hello")
            url = mock_post.call_args[0][0]
            assert "testtoken" in url
            assert "sendMessage" in url

    def test_send_includes_chat_id_and_text(self):
        notifier = self._notifier()
        mock_resp = MagicMock()
        mock_resp.ok = True

        with patch("src.notifier.requests.post", return_value=mock_resp) as mock_post:
            notifier._send("test message")
            payload = mock_post.call_args[1]["json"]
            assert payload["chat_id"] == "987654"
            assert payload["text"] == "test message"

    def test_send_does_not_raise_on_http_error(self):
        notifier = self._notifier()
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"

        with patch("src.notifier.requests.post", return_value=mock_resp):
            notifier._send("test")  # must not raise

    def test_send_does_not_raise_on_network_error(self):
        import requests as req_lib
        notifier = self._notifier()

        with patch("src.notifier.requests.post", side_effect=req_lib.ConnectionError("refused")):
            notifier._send("test")  # must not raise

    def test_notify_pipeline_calls_send_once(self):
        notifier = self._notifier()
        result = _make_pipeline_result(signal=_make_signal(), risk=_make_risk())

        with patch.object(notifier, "_send") as mock_send:
            notifier.notify_pipeline(result)
            mock_send.assert_called_once()

    def test_error_message_html_bold(self):
        """notify_error wraps [ERROR] in HTML bold tags."""
        notifier = TelegramNotifier(bot_token="tok", chat_id="123")
        captured = []
        with patch.object(notifier, "_send", side_effect=captured.append):
            notifier.notify_error("disk full")
        assert "<b>[ERROR]</b>" in captured[0]
        assert "disk full" in captured[0]

    def test_startup_separator_and_html_bold(self):
        """notify_startup includes separator line and HTML bold for mode."""
        notifier = TelegramNotifier(bot_token="tok", chat_id="123")
        captured = []
        with patch.object(notifier, "_send", side_effect=captured.append):
            notifier.notify_startup("rsi_cross", "SOL/USDT", dry_run=True)
        msg = captured[0]
        assert "---" in msg
        assert "<b>[STARTUP]</b>" in msg
        assert "<b>DRY RUN</b>" in msg
