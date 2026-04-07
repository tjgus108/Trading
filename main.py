"""
Trading Bot 진입점.

사용법:
  python main.py --demo                       # API 키 없이 바로 체험 (대시보드 포함)
  python main.py --demo --tournament          # 토너먼트 후 데모 루프
  python main.py                              # dry_run 1회
  python main.py --live                       # 실거래 1회 (backtest gate 통과 필수)
  python main.py --loop                       # 캔들마다 반복 (Ctrl+C 종료)
  python main.py --loop --live               # 실거래 반복
  python main.py --backtest                   # 백테스트만 실행
  python main.py --tournament                 # 전략 토너먼트 후 승자로 실행
  python main.py --tournament --loop          # 토너먼트 승자로 루프 실행
  python main.py --symbols BTC/USDT ETH/USDT # 멀티 심볼 루프 실행
  python main.py --websocket                  # D2: WebSocket 실시간 피드 사용
  python main.py --walk-forward               # D3: 파라미터 자동 최적화 후 실행
  python main.py --config path/to/cfg.yaml
"""

import argparse
import sys

from src.dashboard import Dashboard, MultiStatusProvider, OrchestratorStatusProvider
from src.logging_setup import setup_logging
from src.multi_bot import MultiBot, SymbolConfig
from src.orchestrator import BotOrchestrator, OrchestratorError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--demo", action="store_true",
                        help="API 키 없이 가짜 데이터로 실행. 대시보드 자동 시작.")
    parser.add_argument("--live", action="store_true", help="실거래 모드")
    parser.add_argument("--loop", action="store_true", help="캔들마다 반복 실행")
    parser.add_argument("--backtest", action="store_true", help="백테스트만 실행")
    parser.add_argument("--tournament", action="store_true", help="전략 토너먼트 후 승자로 실행")
    parser.add_argument("--symbols", nargs="+", metavar="SYMBOL",
                        help="멀티 심볼 모드 (예: BTC/USDT ETH/USDT)")
    parser.add_argument("--dashboard", action="store_true",
                        help="HTTP 상태 대시보드 실행 (기본 포트 8080)")
    parser.add_argument("--dashboard-port", type=int, default=8080, metavar="PORT")
    parser.add_argument("--websocket", action="store_true",
                        help="D2: Binance WebSocket 실시간 캔들 피드 사용")
    parser.add_argument("--walk-forward", action="store_true",
                        help="D3: 전략 파라미터 walk-forward 최적화 후 실행")
    parser.add_argument("--ensemble", action="store_true",
                        help="D1: 멀티 LLM 앙상블 활성화 (ANTHROPIC_API_KEY + OPENAI_API_KEY)")
    return parser.parse_args()


def _demo_config():
    """API 키 없이 실행할 수 있는 인메모리 config."""
    from src.config import (AppConfig, ExchangeConfig, LoggingConfig,
                             RiskConfig, TradingConfig)
    return AppConfig(
        exchange=ExchangeConfig(name="binance", sandbox=True),
        trading=TradingConfig(symbol="BTC/USDT", timeframe="1h",
                              max_position_size=0.1, limit=500),
        risk=RiskConfig(max_drawdown=0.20, max_daily_loss=0.05,
                        stop_loss_atr_multiplier=1.5, take_profit_atr_multiplier=3.0,
                        risk_per_trade=0.01),
        logging=LoggingConfig(level="INFO", file="logs/trading.log"),
        strategy="donchian_breakout",
        dry_run=True,
    )


def _load_cfg(args):
    if args.demo:
        return _demo_config()
    from src.config import load_config
    return load_config(args.config)


def main() -> None:
    args = parse_args()
    cfg = _load_cfg(args)
    setup_logging(cfg.logging.level, cfg.logging.file)

    dry_run = not args.live
    show_dashboard = args.dashboard or args.demo
    port = args.dashboard_port

    # ── 멀티 심볼 모드 ────────────────────────────────────────────────────
    if args.symbols:
        symbols = [SymbolConfig(s) for s in args.symbols]
        multi = MultiBot(cfg, symbols)
        try:
            multi.startup(dry_run=dry_run, demo=args.demo)
        except OrchestratorError as e:
            print(f"STARTUP FAILED: {e}")
            sys.exit(1)
        if show_dashboard:
            Dashboard(MultiStatusProvider(multi), port=port).start()
            print(f"Dashboard: http://localhost:{port}")
        multi.run_loop()
        return

    # ── 단일 심볼 모드 ────────────────────────────────────────────────────
    orch = BotOrchestrator(cfg)
    try:
        orch.startup(dry_run=dry_run, demo=args.demo)
    except OrchestratorError as e:
        print(f"STARTUP FAILED: {e}")
        sys.exit(1)

    if show_dashboard:
        Dashboard(OrchestratorStatusProvider(orch), port=port).start()
        print(f"\nDashboard: http://localhost:{port}")
        print(f"  JSON:     http://localhost:{port}/status")
        print(f"  Health:   http://localhost:{port}/health\n")

    # D2: WebSocket 실시간 피드
    if args.websocket:
        _attach_websocket(orch, cfg)

    # D1: 멀티 LLM 앙상블
    if args.ensemble:
        _attach_ensemble(orch)

    if args.backtest:
        result = orch.run_backtest_only()
        print(result.summary())
        sys.exit(0 if result.passed else 1)

    # D3: Walk-forward 파라미터 최적화
    if args.walk_forward:
        _run_walk_forward(orch, cfg)

    if args.tournament:
        result = orch.run_tournament()
        print(result.summary())
        if args.loop or args.demo:
            orch.run_loop()
        else:
            orch.run_once()
        return

    if args.loop or args.demo:
        orch.run_loop()
    else:
        orch.run_once()


def _attach_websocket(orch, cfg) -> None:
    """D2: BinanceWebSocketFeed를 파이프라인에 연결."""
    from src.data.websocket_feed import BinanceWebSocketFeed, WebSocketDataAdapter
    if not BinanceWebSocketFeed.is_websocket_available():
        print("WebSocket: websockets 패키지 없음 (pip install websockets) → REST 사용")
        return
    symbol = cfg.trading.symbol.lower().replace("/", "")
    ws_feed = BinanceWebSocketFeed(symbol=symbol, interval=cfg.trading.timeframe)
    started = ws_feed.start()
    if started and orch._pipeline:
        adapter = WebSocketDataAdapter(ws_feed, rest_feed=orch._data_feed)
        orch._pipeline.data_feed = adapter
        print(f"WebSocket: {symbol}@kline_{cfg.trading.timeframe} 연결됨")


def _attach_ensemble(orch) -> None:
    """D1: MultiLLMEnsemble을 파이프라인에 연결."""
    from src.alpha.ensemble import MultiLLMEnsemble
    ensemble = MultiLLMEnsemble()
    if orch._pipeline:
        orch._pipeline.ensemble = ensemble
        print(f"Ensemble: 활성화 (models={ensemble._claude_client is not None}/{ensemble._openai_client is not None})")


def _run_walk_forward(orch, cfg) -> None:
    """D3: walk-forward 최적화 실행 후 최적 파라미터 출력."""
    from src.backtest.walk_forward import optimize_ema_cross, optimize_donchian, optimize_funding_rate
    summary = orch._data_feed.fetch(cfg.trading.symbol, cfg.trading.timeframe, limit=1000)
    df = summary.df
    print("\n=== Walk-Forward Optimization ===")
    for fn, name in [(optimize_ema_cross, "ema_cross"),
                     (optimize_donchian, "donchian_breakout"),
                     (optimize_funding_rate, "funding_rate")]:
        result = fn(df)
        print(result.summary())
    print("=================================\n")


if __name__ == "__main__":
    main()
