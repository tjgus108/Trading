"""tests/test_notifier.py — Notifier 3계층 알림 스켈레톤 테스트"""
import pytest
from src.exchange.notifier import Notifier, AlertLevel


def test_default_disabled():
    n = Notifier()
    assert n._enabled is False


def test_suppress_returns_false():
    n = Notifier()
    result = n.send("debug msg", AlertLevel.SUPPRESS)
    assert result is False


def test_silent_queues_message():
    n = Notifier()
    result = n.send("daily report", AlertLevel.SILENT)
    assert result is True
    assert n.pending_count == 1


def test_silent_multiple_queue():
    n = Notifier()
    n.send("msg1", AlertLevel.SILENT)
    n.send("msg2", AlertLevel.SILENT)
    n.send("msg3", AlertLevel.SILENT)
    assert n.pending_count == 3


def test_critical_when_disabled_returns_false():
    n = Notifier(enabled=False)
    result = n.send("MAX LOSS", AlertLevel.CRITICAL)
    assert result is False


def test_critical_when_enabled_calls_deliver():
    n = Notifier(enabled=True)
    # _deliver is stub, returns False
    result = n.send("MAX LOSS", AlertLevel.CRITICAL)
    assert result is False  # stub returns False


def test_flush_silent_clears_queue():
    n = Notifier()
    n.send("a", AlertLevel.SILENT)
    n.send("b", AlertLevel.SILENT)
    assert n.pending_count == 2
    n.flush_silent()
    assert n.pending_count == 0


def test_flush_silent_empty_returns_false():
    n = Notifier()
    result = n.flush_silent()
    assert result is False


def test_alert_level_values():
    assert AlertLevel.CRITICAL.value == "CRITICAL"
    assert AlertLevel.SILENT.value == "SILENT"
    assert AlertLevel.SUPPRESS.value == "SUPPRESS"


def test_default_alert_level_is_silent():
    n = Notifier()
    # send without explicit level defaults to SILENT
    result = n.send("some message")
    assert result is True
    assert n.pending_count == 1
