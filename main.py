"""
Trading Bot 진입점.

사용법:
  python main.py                          # dry_run 1회
  python main.py --live                   # 실거래 1회 (backtest gate 통과 필수)
  python main.py --loop                   # 캔들 완성 시각마다 반복 (Ctrl+C 종료)
  python main.py --loop --live            # 실거래 반복
  python main.py --backtest               # 백테스트만 실행
  python main.py --config path/to/cfg.yaml
"""

import argparse
import sys

from src.config import load_config
from src.logging_setup import setup_logging
from src.orchestrator import BotOrchestrator, OrchestratorError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trading Bot")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--live", action="store_true", help="실거래 모드")
    parser.add_argument("--loop", action="store_true", help="캔들마다 반복 실행")
    parser.add_argument("--backtest", action="store_true", help="백테스트만 실행")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    setup_logging(cfg.logging.level, cfg.logging.file)

    dry_run = not args.live
    orch = BotOrchestrator(cfg)

    try:
        orch.startup(dry_run=dry_run)
    except OrchestratorError as e:
        print(f"STARTUP FAILED: {e}")
        sys.exit(1)

    if args.backtest:
        result = orch.run_backtest_only()
        print(result.summary())
        sys.exit(0 if result.passed else 1)

    if args.loop:
        orch.run_loop()
    else:
        orch.run_once()


if __name__ == "__main__":
    main()
