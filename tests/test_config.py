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


def test_risk_per_trade_above_01_raises(tmp_path):
    """risk_per_trade > 0.1이면 ValueError."""
    content = textwrap.dedent("""\
        exchange:
          name: binance
          sandbox: true
        trading:
          symbol: BTC/USDT
          timeframe: 1h
          max_position_size: 0.1
        risk:
          max_drawdown: 0.20
          max_daily_loss: 0.05
          stop_loss: 1.5
          take_profit: 3.0
          risk_per_trade: 0.15
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    with pytest.raises(ValueError, match="risk_per_trade"):
        load_config(str(p))


def test_risk_per_trade_between_005_and_01_warns(tmp_path):
    """0.05 < risk_per_trade <= 0.1이면 UserWarning."""
    content = textwrap.dedent("""\
        exchange:
          name: binance
          sandbox: true
        trading:
          symbol: BTC/USDT
          timeframe: 1h
          max_position_size: 0.1
        risk:
          max_drawdown: 0.20
          max_daily_loss: 0.05
          stop_loss: 1.5
          take_profit: 3.0
          risk_per_trade: 0.07
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    with pytest.warns(UserWarning, match="risk_per_trade"):
        cfg = load_config(str(p))
    assert cfg.risk.risk_per_trade == 0.07


def test_max_position_size_above_05_warns(tmp_path):
    """max_position_size > 0.5이면 UserWarning."""
    content = textwrap.dedent("""\
        exchange:
          name: binance
          sandbox: true
        trading:
          symbol: BTC/USDT
          timeframe: 1h
          max_position_size: 0.8
        risk:
          max_drawdown: 0.20
          max_daily_loss: 0.05
          stop_loss: 1.5
          take_profit: 3.0
          risk_per_trade: 0.01
    """)
    p = tmp_path / "config.yaml"
    p.write_text(content)
    with pytest.warns(UserWarning, match="max_position_size"):
        cfg = load_config(str(p))
    assert cfg.trading.max_position_size == 0.8


# ── 환경 변수 override 테스트 ─────────────────────────────────────────────────

def test_env_overrides_exchange_and_symbol(config_file, monkeypatch):
    """EXCHANGE_NAME, TRADING_SYMBOL 환경 변수가 YAML 값을 덮어씌운다."""
    monkeypatch.setenv("EXCHANGE_NAME", "okx")
    monkeypatch.setenv("TRADING_SYMBOL", "ETH/USDT")
    cfg = load_config(config_file)
    assert cfg.exchange.name == "okx"
    assert cfg.trading.symbol == "ETH/USDT"


def test_env_overrides_risk_and_dry_run(config_file, monkeypatch):
    """RISK_PER_TRADE, RISK_MAX_DRAWDOWN, TRADING_DRY_RUN 환경 변수 override."""
    monkeypatch.setenv("RISK_PER_TRADE", "0.02")
    monkeypatch.setenv("RISK_MAX_DRAWDOWN", "0.10")
    monkeypatch.setenv("TRADING_DRY_RUN", "false")
    cfg = load_config(config_file)
    assert cfg.risk.risk_per_trade == 0.02
    assert cfg.risk.max_drawdown == 0.10
    assert cfg.dry_run is False
