"""Config 로더 단위 테스트."""

import textwrap
from pathlib import Path

import pytest

from src.config import load_config


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
          limit: 500
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


def test_load_config_values(config_file):
    cfg = load_config(config_file)
    assert cfg.exchange.name == "binance"
    assert cfg.exchange.sandbox is True
    assert cfg.trading.symbol == "BTC/USDT"
    assert cfg.trading.timeframe == "1h"
    assert cfg.risk.max_drawdown == 0.20
    assert cfg.risk.risk_per_trade == 0.01
    assert cfg.strategy == "ema_cross"
    assert cfg.dry_run is True


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent/path.yaml")


def test_load_config_defaults(tmp_path):
    """optional 필드 없을 때 기본값 적용 확인."""
    content = textwrap.dedent("""\
        exchange:
          name: bybit
          sandbox: true
        trading:
          symbol: ETH/USDT
          timeframe: 4h
          max_position_size: 0.05
        risk:
          max_drawdown: 0.15
          max_daily_loss: 0.03
          stop_loss: 2.0
          take_profit: 4.0
          risk_per_trade: 0.005
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    cfg = load_config(str(p))
    assert cfg.trading.limit == 500          # default
    assert cfg.risk.max_consecutive_losses == 5  # default
    assert cfg.strategy == "donchian_breakout"   # default
    assert cfg.dry_run is True                   # default
