"""Dashboard 단위 테스트. 실제 HTTP 서버를 띄워서 검증한다."""

import json
import threading
import time
import urllib.request
from unittest.mock import MagicMock

import pytest

from src.dashboard import Dashboard, OrchestratorStatusProvider, _render_html


def _free_port() -> int:
    import socket
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.get_status.return_value = {
        "timestamp": "2026-04-07T00:00:00+00:00",
        "strategy": "ema_cross",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "dry_run": True,
        "cycle_count": 42,
        "open_positions": [],
        "today_pnl": 123.45,
        "daily_summary": "Daily P&L [2026-04-07]: +123.45",
        "circuit_breaker": {"daily_loss": 0.01, "consecutive_losses": 1},
    }
    return provider


@pytest.fixture
def dashboard(mock_provider):
    port = _free_port()
    d = Dashboard(mock_provider, host="127.0.0.1", port=port)
    d.start()
    time.sleep(0.1)
    yield d, port
    d.stop()


def test_health_endpoint(dashboard):
    d, port = dashboard
    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/health")
    data = json.loads(resp.read())
    assert data["ok"] is True


def test_status_endpoint_returns_json(dashboard, mock_provider):
    d, port = dashboard
    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/status")
    data = json.loads(resp.read())
    assert data["strategy"] == "ema_cross"
    assert data["symbol"] == "BTC/USDT"
    assert data["cycle_count"] == 42


def test_root_returns_html(dashboard):
    d, port = dashboard
    resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
    content_type = resp.headers.get("Content-Type", "")
    body = resp.read().decode()
    assert "text/html" in content_type
    assert "Trading Bot" in body
    assert "BTC/USDT" in body


def test_404_on_unknown_path(dashboard):
    d, port = dashboard
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/unknown")
    assert exc.value.code == 404


def test_render_html_contains_key_fields():
    data = {
        "timestamp": "2026-04-07T00:00:00+00:00",
        "strategy": "donchian_breakout",
        "symbol": "ETH/USDT",
        "dry_run": False,
        "cycle_count": 10,
        "open_positions": [
            {
                "symbol": "ETH/USDT",
                "side": "BUY",
                "entry_price": 3000.0,
                "size": 0.1,
                "stop_loss": 2850.0,
                "take_profit": 3300.0,
                "opened_at": "2026-04-07T00:00:00+00:00",
            }
        ],
        "today_pnl": -50.0,
        "daily_summary": "Daily P&L [2026-04-07]: -50.00",
        "circuit_breaker": {"daily_loss": 0.02, "consecutive_losses": 2},
        "bots": [],
    }
    html = _render_html(data)
    assert "donchian_breakout" in html
    assert "ETH/USDT" in html
    assert "LIVE" in html
    assert "3000.00" in html
    assert "-50.00" in html


def test_dashboard_stop_is_idempotent(mock_provider):
    port = _free_port()
    d = Dashboard(mock_provider, host="127.0.0.1", port=port)
    d.start()
    time.sleep(0.05)
    d.stop()
    d.stop()  # 두 번 호출해도 에러 없음
