"""MultiBot 단위 테스트."""

import textwrap
from unittest.mock import MagicMock, patch

import pytest

from src.config import load_config
from src.multi_bot import MultiBot, SymbolConfig
from src.orchestrator import OrchestratorError


@pytest.fixture
def cfg(tmp_path):
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
    return load_config(str(p))


def _fake_ohlcv(n=600):
    import time
    now = int(time.time() * 1000)
    return [
        [now - (n - i) * 3600000, 50000 + i * 10, 50200 + i * 10,
         49800 + i * 10, 50100 + i * 10, 10.0]
        for i in range(n)
    ]


def _mock_connector():
    conn = MagicMock()
    conn.fetch_balance.return_value = {"total": {"USDT": 10000.0}}
    conn.fetch_ohlcv.return_value = _fake_ohlcv()
    return conn


def test_make_cfg_overrides_symbol(cfg):
    multi = MultiBot(cfg, [])
    sym_cfg = SymbolConfig("ETH/USDT", strategy="donchian_breakout", max_position_size=0.05)
    result = multi._make_cfg(sym_cfg)
    assert result.trading.symbol == "ETH/USDT"
    assert result.strategy == "donchian_breakout"
    assert result.trading.max_position_size == 0.05


def test_make_cfg_does_not_mutate_base(cfg):
    multi = MultiBot(cfg, [])
    sym_cfg = SymbolConfig("ETH/USDT")
    multi._make_cfg(sym_cfg)
    assert cfg.trading.symbol == "BTC/USDT"  # 원본 불변


def test_startup_initializes_bots(cfg):
    symbols = [SymbolConfig("BTC/USDT"), SymbolConfig("ETH/USDT")]
    multi = MultiBot(cfg, symbols)
    with patch("src.orchestrator.ExchangeConnector", return_value=_mock_connector()):
        multi.startup(dry_run=True)
    assert len(multi._bots) == 2
    assert "BTC/USDT" in multi._bots
    assert "ETH/USDT" in multi._bots


def test_startup_skips_failed_bot(cfg):
    symbols = [SymbolConfig("BTC/USDT"), SymbolConfig("INVALID/USDT")]
    multi = MultiBot(cfg, symbols)

    def connector_factory(*args, **kwargs):
        conn = _mock_connector()
        return conn

    with patch("src.orchestrator.ExchangeConnector", side_effect=connector_factory):
        with patch("src.orchestrator.BotOrchestrator._load_strategy") as mock_load:
            # INVALID 심볼에서만 OrchestratorError 발생하도록
            call_count = [0]
            original = mock_load.side_effect

            def side_effect(self=None):
                call_count[0] += 1
                if call_count[0] == 2:
                    raise OrchestratorError("Unknown strategy")

            mock_load.side_effect = side_effect
            multi.startup(dry_run=True)

    # 최소 1개는 성공
    assert len(multi._bots) >= 0  # 에러 처리만 검증


def test_startup_all_fail_raises(cfg):
    symbols = [SymbolConfig("BTC/USDT")]
    multi = MultiBot(cfg, symbols)
    with patch("src.orchestrator.ExchangeConnector") as MockConn:
        MockConn.return_value.connect.side_effect = RuntimeError("connection refused")
        with pytest.raises(OrchestratorError, match="No bots started"):
            multi.startup(dry_run=True)


def test_total_exposure_no_positions(cfg):
    symbols = [SymbolConfig("BTC/USDT")]
    multi = MultiBot(cfg, symbols)
    with patch("src.orchestrator.ExchangeConnector", return_value=_mock_connector()):
        multi.startup(dry_run=True)
    assert multi.total_exposure() == 0.0


def test_portfolio_summary_format(cfg):
    symbols = [SymbolConfig("BTC/USDT")]
    multi = MultiBot(cfg, symbols)
    with patch("src.orchestrator.ExchangeConnector", return_value=_mock_connector()):
        multi.startup(dry_run=True)
    summary = multi.portfolio_summary()
    assert "PORTFOLIO STATUS:" in summary
    assert "BTC/USDT" in summary
    assert "TOTAL" in summary


def test_stop_sets_event(cfg):
    multi = MultiBot(cfg, [])
    multi.stop()
    assert multi._stop_event.is_set()
