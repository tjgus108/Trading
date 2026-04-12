"""
Config 로더: config.yaml → dataclass.
환경변수(.env)와 YAML 설정을 통합한다.

환경 변수 override 목록 (YAML보다 우선):
  TRADING_SYMBOL          → trading.symbol
  TRADING_TIMEFRAME       → trading.timeframe
  TRADING_DRY_RUN         → dry_run  (true/false)
  EXCHANGE_NAME           → exchange.name
  EXCHANGE_SANDBOX        → exchange.sandbox (true/false)
  RISK_PER_TRADE          → risk.risk_per_trade (float)
  RISK_MAX_DRAWDOWN       → risk.max_drawdown (float)
  RISK_MAX_DAILY_LOSS     → risk.max_daily_loss (float)
  TELEGRAM_BOT_TOKEN      → telegram.bot_token
  TELEGRAM_CHAT_ID        → telegram.chat_id

API 키는 반드시 환경 변수로만 관리할 것 (config.yaml에 절대 기입 금지):
  EXCHANGE_API_KEY
  EXCHANGE_API_SECRET
"""

import logging
import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


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


def _env_bool(key: str, default: bool) -> bool:
    """환경 변수를 bool로 변환. 'true'/'1' → True, 'false'/'0' → False."""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes")


def _env_float(key: str, default: float) -> float:
    """환경 변수를 float으로 변환. 파싱 실패 시 default 반환."""
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        warnings.warn(
            f"환경 변수 {key}='{val}'을 float으로 변환할 수 없어 기본값 {default}를 사용합니다.",
            UserWarning,
            stacklevel=4,
        )
        return default


def _apply_env_overrides(cfg: AppConfig) -> AppConfig:
    """환경 변수로 config 값을 override한다. 환경 변수가 없으면 YAML 값 유지."""
    # exchange
    cfg.exchange.name = os.environ.get("EXCHANGE_NAME", cfg.exchange.name)
    cfg.exchange.sandbox = _env_bool("EXCHANGE_SANDBOX", cfg.exchange.sandbox)

    # trading
    cfg.trading.symbol = os.environ.get("TRADING_SYMBOL", cfg.trading.symbol)
    cfg.trading.timeframe = os.environ.get("TRADING_TIMEFRAME", cfg.trading.timeframe)

    # risk
    cfg.risk.risk_per_trade = _env_float("RISK_PER_TRADE", cfg.risk.risk_per_trade)
    cfg.risk.max_drawdown = _env_float("RISK_MAX_DRAWDOWN", cfg.risk.max_drawdown)
    cfg.risk.max_daily_loss = _env_float("RISK_MAX_DAILY_LOSS", cfg.risk.max_daily_loss)

    # top-level
    cfg.dry_run = _env_bool("TRADING_DRY_RUN", cfg.dry_run)

    # telegram (override bot_token / chat_id if env vars present)
    if cfg.telegram is not None:
        cfg.telegram.bot_token = os.environ.get(
            "TELEGRAM_BOT_TOKEN", cfg.telegram.bot_token
        )
        cfg.telegram.chat_id = os.environ.get(
            "TELEGRAM_CHAT_ID", cfg.telegram.chat_id
        )

    return cfg


def _validate_config(cfg: AppConfig) -> None:
    """위험 파라미터 검증. 임계값 초과 시 경고 또는 에러."""
    rpt = cfg.risk.risk_per_trade
    if rpt > 0.1:
        raise ValueError(
            f"risk_per_trade={rpt} exceeds maximum allowed 0.1 (10%). "
            "Set a safer value."
        )
    if rpt > 0.05:
        warnings.warn(
            f"risk_per_trade={rpt} is above 0.05 (5%). "
            "Consider reducing to limit per-trade exposure.",
            UserWarning,
            stacklevel=3,
        )

    mps = cfg.trading.max_position_size
    if mps > 0.5:
        warnings.warn(
            f"max_position_size={mps} exceeds 0.5 (50%). "
            "High concentration risk.",
            UserWarning,
            stacklevel=3,
        )



# ---------------------------------------------------------------------------
# Migration helper
# ---------------------------------------------------------------------------
_RISK_KEY_ALIASES: dict[str, str] = {
    # old key → new key (for raw["risk"] dict)
    "stop_loss": "stop_loss_atr_multiplier",
    "take_profit": "take_profit_atr_multiplier",
}

_RISK_DEFAULTS: dict[str, object] = {
    "max_drawdown": 0.20,
    "max_daily_loss": 0.05,
    "stop_loss_atr_multiplier": 1.5,
    "take_profit_atr_multiplier": 3.0,
    "risk_per_trade": 0.01,
    "max_consecutive_losses": 5,
    "flash_crash_pct": 0.10,
}

_TRADING_DEFAULTS: dict[str, object] = {
    "max_position_size": 0.10,
    "limit": 500,
}


def migrate_config(raw: dict) -> dict:
    """구버전 config dict를 신버전 스키마로 in-place 마이그레이션한다.

    변환 내용:
    - risk.stop_loss        → risk.stop_loss_atr_multiplier
    - risk.take_profit      → risk.take_profit_atr_multiplier
    - 누락된 risk / trading 필드에 기본값 자동 삽입
    - 변환이 발생하면 UserWarning 발생

    Parameters
    ----------
    raw : dict
        yaml.safe_load() 결과 dict (in-place 수정).

    Returns
    -------
    dict
        마이그레이션된 동일 dict.
    """
    rsk: dict = raw.setdefault("risk", {})

    # 구버전 키 → 신버전 키 이름 변환
    for old_key, new_key in _RISK_KEY_ALIASES.items():
        if old_key in rsk and new_key not in rsk:
            warnings.warn(
                f"config: 구버전 키 'risk.{old_key}'를 'risk.{new_key}'로 마이그레이션합니다.",
                UserWarning,
                stacklevel=3,
            )
            rsk[new_key] = rsk.pop(old_key)

    # 누락 필드 기본값 채우기 (risk) — 디버그 로그만, 기본값은 정상 동작
    for key, default in _RISK_DEFAULTS.items():
        if key not in rsk:
            logger.debug("config: 'risk.%s' 누락 — 기본값 %r 사용.", key, default)
            rsk[key] = default

    # 누락 필드 기본값 채우기 (trading)
    trd: dict = raw.setdefault("trading", {})
    for key, default in _TRADING_DEFAULTS.items():
        if key not in trd:
            logger.debug("config: 'trading.%s' 누락 — 기본값 %r 사용.", key, default)
            trd[key] = default

    return raw

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

    migrate_config(raw)

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

    cfg = AppConfig(
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
            stop_loss_atr_multiplier=rsk.get("stop_loss_atr_multiplier", 1.5),
            take_profit_atr_multiplier=rsk.get("take_profit_atr_multiplier", 3.0),
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

    _apply_env_overrides(cfg)
    _validate_config(cfg)
    return cfg
