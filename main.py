"""
Trading Bot 진입점.

사용법:
  python main.py                          # dry_run (config.yaml 기준)
  python main.py --live                   # 실거래 (sandbox=false 필요)
  python main.py --backtest               # 백테스트만 실행
  python main.py --loop                   # 캔들 완성 시각에 맞춰 반복 실행
  python main.py --config path/to/cfg.yaml
"""

import argparse
import logging
import sys
import threading

from src.config import load_config
from src.logging_setup import setup_logging
from src.exchange.connector import ExchangeConnector
from src.data.feed import DataFeed
from src.risk.manager import CircuitBreaker, RiskManager
from src.pipeline.runner import TradingPipeline
from src.strategy.ema_cross import EmaCrossStrategy
from src.strategy.donchian_breakout import DonchianBreakoutStrategy
from src.backtest.engine import BacktestEngine
from src.notifier import TelegramNotifier
from src.scheduler import CandleScheduler

logger = logging.getLogger(__name__)

STRATEGIES = {
    "ema_cross": EmaCrossStrategy,
    "donchian_breakout": DonchianBreakoutStrategy,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument("--config", default="config/config.yaml", help="설정 파일 경로")
    parser.add_argument("--live", action="store_true", help="실거래 모드 (dry_run 무시)")
    parser.add_argument("--backtest", action="store_true", help="백테스트만 실행하고 종료")
    parser.add_argument("--loop", action="store_true", help="캔들 완성 시각에 맞춰 반복 실행 (Ctrl+C로 종료)")
    return parser.parse_args()


def build_components(cfg):
    """설정으로부터 컴포넌트 조립."""
    connector = ExchangeConnector(
        exchange_name=cfg.exchange.name,
        sandbox=cfg.exchange.sandbox,
    )
    connector.connect()

    data_feed = DataFeed(connector)

    circuit_breaker = CircuitBreaker(
        max_daily_loss=cfg.risk.max_daily_loss,
        max_drawdown=cfg.risk.max_drawdown,
        max_consecutive_losses=cfg.risk.max_consecutive_losses,
        flash_crash_pct=cfg.risk.flash_crash_pct,
    )
    risk_manager = RiskManager(
        risk_per_trade=cfg.risk.risk_per_trade,
        atr_multiplier_sl=cfg.risk.stop_loss_atr_multiplier,
        atr_multiplier_tp=cfg.risk.take_profit_atr_multiplier,
        max_position_size=cfg.trading.max_position_size,
        circuit_breaker=circuit_breaker,
    )

    strategy_cls = STRATEGIES.get(cfg.strategy)
    if strategy_cls is None:
        raise ValueError(f"Unknown strategy: {cfg.strategy}. Choose from: {list(STRATEGIES)}")
    strategy = strategy_cls()

    return connector, data_feed, risk_manager, strategy


def run_backtest(cfg, data_feed, strategy) -> bool:
    """백테스트 실행. PASS 여부 반환."""
    logger.info("=== Backtest: %s %s %s ===", strategy.name, cfg.trading.symbol, cfg.trading.timeframe)
    summary = data_feed.fetch(cfg.trading.symbol, cfg.trading.timeframe, limit=1000)
    engine = BacktestEngine(
        atr_multiplier_sl=cfg.risk.stop_loss_atr_multiplier,
        atr_multiplier_tp=cfg.risk.take_profit_atr_multiplier,
    )
    result = engine.run(strategy, summary.df)
    print(result.summary())
    return result.passed


def build_notifier(cfg) -> TelegramNotifier:
    """설정으로부터 TelegramNotifier 생성."""
    tg = cfg.telegram
    if tg is None:
        return TelegramNotifier(enabled=False)
    return TelegramNotifier(
        bot_token=tg.bot_token,
        chat_id=tg.chat_id,
        enabled=tg.enabled,
    )


def run_pipeline(cfg, connector, data_feed, risk_manager, strategy, dry_run: bool, notifier: TelegramNotifier) -> None:
    """파이프라인 1회 실행."""
    pipeline = TradingPipeline(
        connector=connector,
        data_feed=data_feed,
        strategy=strategy,
        risk_manager=risk_manager,
        symbol=cfg.trading.symbol,
        timeframe=cfg.trading.timeframe,
        dry_run=dry_run,
    )

    logger.info(
        "Running pipeline: %s %s %s dry_run=%s",
        strategy.name,
        cfg.trading.symbol,
        cfg.trading.timeframe,
        dry_run,
    )
    result = pipeline.run()

    # 콘솔 출력
    print(f"\nPIPELINE: {result.pipeline_step}")
    print(f"STATUS:   {result.status}")
    if result.signal:
        print(f"SIGNAL:   {result.signal.action.value} @ {result.signal.entry_price:.2f}  ({result.signal.confidence.value})")
        print(f"  bull: {result.signal.bull_case}")
        print(f"  bear: {result.signal.bear_case}")
    if result.risk:
        print(f"RISK:     {result.risk.status.value}", end="")
        if result.risk.reason:
            print(f" — {result.risk.reason}", end="")
        print()
        if result.risk.position_size:
            print(f"  size={result.risk.position_size}  SL={result.risk.stop_loss}  TP={result.risk.take_profit}")
    if result.execution:
        print(f"EXEC:     {result.execution.get('status')}")
    if result.notes:
        print(f"NOTES:    {' | '.join(result.notes)}")
    if result.error:
        print(f"ERROR:    {result.error}")

    # Telegram 알림
    notifier.notify_pipeline(result)

    # WORKLOG 기록
    _append_worklog(result)


def _append_worklog(result) -> None:
    try:
        with open(".claude-state/WORKLOG.md", "a") as f:
            f.write("\n" + result.log_line())
    except OSError:
        pass


def main() -> None:
    args = parse_args()

    cfg = load_config(args.config)
    setup_logging(cfg.logging.level, cfg.logging.file)

    logger.info("Trading Bot starting — strategy=%s symbol=%s", cfg.strategy, cfg.trading.symbol)

    notifier = build_notifier(cfg)

    try:
        connector, data_feed, risk_manager, strategy = build_components(cfg)
    except Exception as e:
        logger.error("Startup failed: %s", e)
        notifier.notify_error(f"Startup failed: {e}")
        sys.exit(1)

    if args.backtest:
        passed = run_backtest(cfg, data_feed, strategy)
        sys.exit(0 if passed else 1)

    dry_run = not args.live
    if args.live:
        logger.warning("LIVE MODE — real orders will be submitted")

    notifier.notify_startup(
        strategy=cfg.strategy,
        symbol=cfg.trading.symbol,
        dry_run=dry_run,
    )

    if args.loop:
        # ── 반복 실행 (스케줄러 모드) ───────────────────────────────────
        stop_event = threading.Event()

        def _pipeline_fn():
            run_pipeline(cfg, connector, data_feed, risk_manager, strategy, dry_run=dry_run, notifier=notifier)

        scheduler = CandleScheduler()
        logger.info(
            "Loop mode — timeframe=%s  (Ctrl+C to stop)",
            cfg.trading.timeframe,
        )
        try:
            scheduler.run_loop(_pipeline_fn, cfg.trading.timeframe, stop_event)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received — stopping scheduler")
            stop_event.set()
        logger.info("Trading Bot stopped gracefully")
    else:
        # ── 1회 실행 ───────────────────────────────────────────────────
        try:
            run_pipeline(cfg, connector, data_feed, risk_manager, strategy, dry_run=dry_run, notifier=notifier)
        except Exception as e:
            logger.error("Pipeline error: %s", e)
            notifier.notify_error(f"Pipeline error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
