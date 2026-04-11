"""Tests for LLMAnalyst robustness: timeout, empty response, unexpected text."""

import pytest
from unittest.mock import MagicMock, patch
from src.alpha.llm_analyst import LLMAnalyst


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(text: str):
    """Build a fake anthropic Messages response."""
    msg = MagicMock()
    content_block = MagicMock()
    content_block.text = text
    msg.content = [content_block]
    return msg


def _make_empty_response():
    """Simulate response with no content blocks."""
    msg = MagicMock()
    msg.content = []
    return msg


# ---------------------------------------------------------------------------
# analyze_signal
# ---------------------------------------------------------------------------

class TestAnalyzeSignal:
    def _analyst(self):
        """Create analyst with a mock client, bypassing the import check."""
        analyst = LLMAnalyst(use_haiku=True, enabled=False)
        # Force-enable and inject mock client directly
        analyst._enabled = True
        analyst._client = MagicMock()
        return analyst

    def test_returns_text_on_success(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_response("Looks bullish.")
        result = analyst.analyze_signal("BTC/USDT", "BUY", "RSI oversold")
        assert result == "Looks bullish."

    def test_returns_empty_on_api_exception(self):
        analyst = self._analyst()
        analyst._client.messages.create.side_effect = Exception("timeout")
        result = analyst.analyze_signal("BTC/USDT", "BUY", "RSI oversold")
        assert result == ""

    def test_returns_empty_on_empty_content(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_empty_response()
        result = analyst.analyze_signal("BTC/USDT", "SELL", "MACD cross")
        assert result == ""

    def test_returns_empty_on_blank_text(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_response("   ")
        result = analyst.analyze_signal("BTC/USDT", "HOLD", "neutral")
        assert result == ""

    def test_disabled_returns_mock(self):
        analyst = LLMAnalyst(enabled=False)
        result = analyst.analyze_signal("BTC/USDT", "BUY", "reason")
        assert "[Mock LLM]" in result


# ---------------------------------------------------------------------------
# classify_news_risk
# ---------------------------------------------------------------------------

class TestClassifyNewsRisk:
    def _analyst(self):
        analyst = LLMAnalyst(enabled=False)
        analyst._enabled = True
        analyst._client = MagicMock()
        return analyst

    def test_valid_classification(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_response("HIGH")
        assert analyst.classify_news_risk("Exchange hacked") == "HIGH"

    def test_api_exception_returns_none(self):
        analyst = self._analyst()
        analyst._client.messages.create.side_effect = TimeoutError("timed out")
        assert analyst.classify_news_risk("Some headline") == "NONE"

    def test_empty_content_returns_none(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_empty_response()
        assert analyst.classify_news_risk("Some headline") == "NONE"

    def test_unexpected_text_returns_none(self):
        analyst = self._analyst()
        analyst._client.messages.create.return_value = _make_response("CRITICAL")
        assert analyst.classify_news_risk("Weird response") == "NONE"

    def test_disabled_returns_none(self):
        analyst = LLMAnalyst(enabled=False)
        assert analyst.classify_news_risk("Any headline") == "NONE"
