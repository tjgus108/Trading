"""
Config 로더: config.yaml → dataclass.
환경변수(.env)와 YAML 설정을 통합한다.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class ExchangeConfig:
    name: str
    sandbox: bool


@dataclass
class TradingConfig:
    symbol: str
    timeframe: str
    max_position_size: float
    limit: int = 1000  # OHLCV 캔들 수


@dataclass
class RiskConfig:
    max_drawdown: float
    max_daily_loss: float
    stop_loss_atr_multiplier: float
    take_profit_atr_multiplier: float
    risk_per_trade: float
    max_consecutive_losses: int = 5
    flash_crash_pct: float = 0.10


@dataclass
class LoggingConfig:
    level: str
    file: str


@dataclass
class TelegramConfig:
    enabled: bool
    bot_token: str
    chat_id: str


@dataclass
class AppConfig:
    exchange: ExchangeConfig
    trading: TradingConfig
    risk: RiskConfig
    logging: LoggingConfig
    strategy: str = "donchian_breakout"  # "ema_cross" | "donchian_breakout"
    dry_run: bool = True
    telegram: Optional[TelegramConfig] = None


def load_config(path: str = "config/config.yaml") -> AppConfig:
    load_dotenv()

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            "Copy config/config.example.yaml to config/config.yaml and edit it."
        )

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    exc = raw["exchange"]
    trd = raw["trading"]
    rsk = raw["risk"]
    log = raw.get("logging", {})
    tg = raw.get("telegram")

    telegram_cfg: Optional[TelegramConfig] = None
    if tg is not None:
        telegram_cfg = TelegramConfig(
            enabled=tg.get("enabled", False),
            bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", tg.get("bot_token", "")),
            chat_id=os.environ.get("TELEGRAM_CHAT_ID", tg.get("chat_id", "")),
        )

    return AppConfig(
        exchange=ExchangeConfig(
            name=exc["name"],
            sandbox=exc.get("sandbox", True),
        ),
        trading=TradingConfig(
            symbol=trd["symbol"],
            timeframe=trd["timeframe"],
            max_position_size=trd.get("max_position_size", 0.10),
            limit=trd.get("limit", 500),
        ),
        risk=RiskConfig(
            max_drawdown=rsk.get("max_drawdown", 0.20),
            max_daily_loss=rsk.get("max_daily_loss", 0.05),
            stop_loss_atr_multiplier=rsk.get("stop_loss", 1.5),
            take_profit_atr_multiplier=rsk.get("take_profit", 3.0),
            risk_per_trade=rsk.get("risk_per_trade", 0.01),
            max_consecutive_losses=rsk.get("max_consecutive_losses", 5),
            flash_crash_pct=rsk.get("flash_crash_pct", 0.10),
        ),
        logging=LoggingConfig(
            level=log.get("level", "INFO"),
            file=log.get("file", "logs/trading.log"),
        ),
        strategy=raw.get("strategy", "donchian_breakout"),
        dry_run=raw.get("dry_run", True),
        telegram=telegram_cfg,
    )
