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


# ── Walk-Forward 토너먼트 통합 테스트 ────────────────────────────────────

def _make_backtest_result(sharpe: float, passed: bool = True):
    r = MagicMock()
    r.sharpe_ratio = sharpe
    r.passed = passed
    r.fail_reasons = []
    r.total_return = 0.05
    r.win_rate = 0.55
    r.max_drawdown = 0.05
    r.total_trades = 10
    return r


def test_tournament_wf_stable_winner_keeps_first(cfg, mock_connector):
    """WF 안정적이면 1위 전략 그대로 유지."""
    orch = _make_orch(cfg, mock_connector)

    from src.backtest.walk_forward import WalkForwardValidationResult

    wf_result = WalkForwardValidationResult(
        windows=5,
        mean_return=0.03,
        std_return=0.01,
        win_rate=0.8,
        consistency_score=0.8,  # >= 0.5 → STABLE
        results=[],
    )

    ranked = [
        ("ema_cross", _make_backtest_result(1.5)),
        ("donchian_breakout", _make_backtest_result(1.2)),
    ]

    import pandas as pd, numpy as np
    n = 300
    df = pd.DataFrame({
        "open": np.ones(n) * 50000,
        "high": np.ones(n) * 50200,
        "low": np.ones(n) * 49800,
        "close": np.ones(n) * 50100,
        "volume": np.ones(n) * 10.0,
    })
    mock_feed_result = MagicMock()
    mock_feed_result.df = df

    with patch.object(orch, "_run_backtest", side_effect=lambda s: _make_backtest_result(1.5)):
        with patch("src.backtest.walk_forward.WalkForwardValidator") as MockWFV:
            MockWFV.return_value.validate.return_value = wf_result
            with patch.object(orch._data_feed, "fetch", return_value=mock_feed_result):
                result = orch.run_tournament(candidates=["ema_cross"])

    assert result.wf_stable is True
    assert result.wf_fallback is False
    assert result.winner == "ema_cross"


def test_tournament_wf_unstable_falls_back_to_second(cfg, mock_connector):
    """WF 불안정하면 2위 전략으로 fallback."""
    orch = _make_orch(cfg, mock_connector)

    from src.backtest.walk_forward import WalkForwardValidationResult

    wf_result = WalkForwardValidationResult(
        windows=5,
        mean_return=-0.01,
        std_return=0.05,
        win_rate=0.2,
        consistency_score=0.2,  # < 0.5 → UNSTABLE
        results=[],
    )

    backtest_map = {
        "ema_cross": _make_backtest_result(1.5),
        "donchian_breakout": _make_backtest_result(1.2),
    }

    def fake_run_backtest(strategy):
        return backtest_map.get(strategy.name, _make_backtest_result(0.5))

    import pandas as pd, numpy as np
    n = 300
    df = pd.DataFrame({
        "open": np.ones(n) * 50000,
        "high": np.ones(n) * 50200,
        "low": np.ones(n) * 49800,
        "close": np.ones(n) * 50100,
        "volume": np.ones(n) * 10.0,
    })
    mock_feed_result = MagicMock()
    mock_feed_result.df = df

    with patch.object(orch, "_run_backtest", side_effect=fake_run_backtest):
        with patch("src.backtest.walk_forward.WalkForwardValidator") as MockWFV:
            MockWFV.return_value.validate.return_value = wf_result
            with patch.object(orch._data_feed, "fetch", return_value=mock_feed_result):
                result = orch.run_tournament(candidates=["ema_cross", "donchian_breakout"])

    assert result.wf_stable is False
    assert result.wf_fallback is True
    assert result.winner == "donchian_breakout"


def test_tournament_wf_skipped_when_insufficient_data(cfg, mock_connector):
    """WF 데이터 < 250봉이면 wf_stable=None, 1위 전략 그대로 유지."""
    orch = _make_orch(cfg, mock_connector)

    import pandas as pd, numpy as np
    n = 100  # 250 미만 → WF 건너뜀
    df = pd.DataFrame({
        "open": np.ones(n) * 50000,
        "high": np.ones(n) * 50200,
        "low": np.ones(n) * 49800,
        "close": np.ones(n) * 50100,
        "volume": np.ones(n) * 10.0,
    })
    mock_feed_result = MagicMock()
    mock_feed_result.df = df

    with patch.object(orch, "_run_backtest", return_value=_make_backtest_result(1.5)):
        with patch.object(orch._data_feed, "fetch", return_value=mock_feed_result):
            result = orch.run_tournament(candidates=["ema_cross"])

    assert result.wf_stable is None      # WF 미실행
    assert result.wf_fallback is False
    assert result.winner == "ema_cross"


def test_tournament_wf_exception_is_non_fatal(cfg, mock_connector):
    """WF 검증 중 예외 발생 시 1위 전략 그대로 유지하고 tournament 정상 완료."""
    orch = _make_orch(cfg, mock_connector)

    import pandas as pd, numpy as np
    n = 300
    df = pd.DataFrame({
        "open": np.ones(n) * 50000,
        "high": np.ones(n) * 50200,
        "low": np.ones(n) * 49800,
        "close": np.ones(n) * 50100,
        "volume": np.ones(n) * 10.0,
    })
    mock_feed_result = MagicMock()
    mock_feed_result.df = df

    with patch.object(orch, "_run_backtest", return_value=_make_backtest_result(1.5)):
        with patch("src.backtest.walk_forward.WalkForwardValidator") as MockWFV:
            MockWFV.return_value.validate.side_effect = RuntimeError("WF crash")
            with patch.object(orch._data_feed, "fetch", return_value=mock_feed_result):
                result = orch.run_tournament(candidates=["ema_cross"])

    # WF 예외여도 토너먼트 결과 반환, 1위 유지
    assert result.winner == "ema_cross"
    assert result.wf_fallback is False


# ── DrawdownMonitor AlertLevel 연동 테스트 ──────────────────────────────────

def test_drawdown_halt_blocks_run_once(cfg, mock_connector):
    """DrawdownMonitor가 HALT 상태이면 run_once가 BLOCKED PipelineResult를 반환한다."""
    from src.risk.drawdown_monitor import AlertLevel

    orch = _make_orch(cfg, mock_connector)

    halted_status = MagicMock()
    halted_status.halted = True
    halted_status.alert_level = AlertLevel.HALT
    halted_status.reason = "주간 낙폭 7.5% ≥ 한계 7.0% — 거래 중단"

    with patch.object(orch._drawdown_monitor, "update", return_value=halted_status):
        result = orch.run_once()

    assert result.status == "BLOCKED"
    assert "HALT" in result.notes[0]
    assert not orch._stop_event.is_set()


def test_force_liquidate_sets_stop_event(cfg, mock_connector):
    """FORCE_LIQUIDATE 레벨이면 run_once가 BLOCKED + _stop_event를 세팅한다."""
    from src.risk.drawdown_monitor import AlertLevel

    orch = _make_orch(cfg, mock_connector)

    fl_status = MagicMock()
    fl_status.halted = True
    fl_status.alert_level = AlertLevel.FORCE_LIQUIDATE
    fl_status.reason = "월간 낙폭 16.0% ≥ 한계 15.0% — 강제 청산"

    with patch.object(orch._drawdown_monitor, "update", return_value=fl_status):
        result = orch.run_once()

    assert result.status == "BLOCKED"
    assert "FORCE_LIQUIDATE" in result.notes[0]
    assert orch._stop_event.is_set()
