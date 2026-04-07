"""BotOrchestrator 단위 테스트. 거래소 연결 없이 동작한다."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import load_config
from src.orchestrator import BotOrchestrator, OrchestratorError
from src.pipeline.runner import PipelineResult
from src.strategy.base import Action, Confidence, Signal
from src.risk.manager import RiskResult, RiskStatus


@pytest.fixture
def config_file(tmp_path):
    content = textwrap.dedent("""\
        exchange:
          name: binance
          sandbox: true
        trading:
          symbol: BTC/USDT
          timeframe: 1h
          max_position_size: 0.1
        strategy: ema_cross
        dry_run: true
        risk:
          max_drawdown: 0.20
          max_daily_loss: 0.05
          stop_loss: 1.5
          take_profit: 3.0
          risk_per_trade: 0.01
        logging:
          level: INFO
          file: logs/trading.log
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    return str(p)


@pytest.fixture
def cfg(config_file):
    return load_config(config_file)


@pytest.fixture
def mock_connector():
    conn = MagicMock()
    conn.fetch_balance.return_value = {"total": {"USDT": 10000.0}}
    conn.fetch_ohlcv.return_value = _fake_ohlcv(600)
    return conn


def _fake_ohlcv(n: int) -> list:
    import time
    now = int(time.time() * 1000)
    interval = 3600 * 1000
    return [
        [now - (n - i) * interval, 50000 + i * 10, 50200 + i * 10, 49800 + i * 10, 50100 + i * 10, 10.0]
        for i in range(n)
    ]


def _make_orch(cfg, connector) -> BotOrchestrator:
    orch = BotOrchestrator(cfg)
    with patch("src.orchestrator.ExchangeConnector", return_value=connector):
        orch.startup(dry_run=True)
    return orch


def test_startup_assert_ready(cfg, mock_connector):
    orch = _make_orch(cfg, mock_connector)
    assert orch._pipeline is not None
    assert orch._strategy is not None
    assert orch._risk_manager is not None


def test_run_once_before_startup_raises(cfg):
    orch = BotOrchestrator(cfg)
    with pytest.raises(OrchestratorError, match="startup"):
        orch.run_once()


def test_unknown_strategy_raises(tmp_path):
    content = textwrap.dedent("""\
        exchange:
          name: binance
          sandbox: true
        trading:
          symbol: BTC/USDT
          timeframe: 1h
          max_position_size: 0.1
        strategy: nonexistent_strategy
        risk:
          max_drawdown: 0.20
          max_daily_loss: 0.05
          stop_loss: 1.5
          take_profit: 3.0
          risk_per_trade: 0.01
        logging:
          level: INFO
          file: logs/trading.log
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    cfg_bad = load_config(str(p))
    orch = BotOrchestrator(cfg_bad)
    conn = MagicMock()
    conn.fetch_ohlcv.return_value = _fake_ohlcv(600)
    with pytest.raises(OrchestratorError, match="Unknown strategy"):
        with patch("src.orchestrator.ExchangeConnector", return_value=conn):
            orch.startup(dry_run=True)


def test_run_once_returns_pipeline_result(cfg, mock_connector):
    orch = _make_orch(cfg, mock_connector)
    result = orch.run_once()
    assert isinstance(result, PipelineResult)
    assert result.status in ("OK", "BLOCKED", "ERROR")


def test_backtest_gate_blocks_live_on_fail(cfg, mock_connector):
    """backtest FAIL 전략은 live startup에서 OrchestratorError."""
    orch = BotOrchestrator(cfg)
    mock_result = MagicMock()
    mock_result.passed = False
    mock_result.fail_reasons = ["sharpe 0.50 < 1.0"]
    mock_result.summary.return_value = "BACKTEST_RESULT:\n  verdict: FAIL"

    with patch("src.orchestrator.ExchangeConnector", return_value=mock_connector):
        with patch.object(orch, "_run_backtest", return_value=mock_result):
            with pytest.raises(OrchestratorError, match="Backtest gate FAILED"):
                orch.startup(dry_run=False)


def test_backtest_gate_skipped_in_dry_run(cfg, mock_connector):
    """dry_run=True이면 backtest gate 없이 startup 완료."""
    orch = BotOrchestrator(cfg)
    with patch("src.orchestrator.ExchangeConnector", return_value=mock_connector):
        with patch.object(orch, "_backtest_gate") as mock_gate:
            orch.startup(dry_run=True)
            mock_gate.assert_not_called()


def test_stop_signal_stops_loop(cfg, mock_connector):
    """stop() 호출 시 run_loop가 즉시 종료."""
    orch = _make_orch(cfg, mock_connector)
    orch._stop_event.set()  # 미리 set → loop 즉시 탈출

    called = []
    def fake_run_loop(fn, tf, stop):
        if stop.is_set():
            return
        called.append(1)

    with patch("src.orchestrator.CandleScheduler") as MockSched:
        MockSched.return_value.run_loop.side_effect = fake_run_loop
        orch.run_loop()

    assert called == []


def test_notifier_disabled_without_telegram_config(cfg, mock_connector):
    orch = _make_orch(cfg, mock_connector)
    assert orch._notifier is not None
    assert orch._notifier._enabled is False
