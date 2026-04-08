#!/usr/bin/env python3
"""
standalone ML training script.

usage:
  python scripts/train_ml.py [--symbol BTC/USDT] [--timeframe 1h] [--model rf|lstm] [--limit 1000] [--demo]

--demo: MockExchangeConnector 사용 (API 키 불필요)
--model rf:   WalkForwardTrainer (RandomForest), models/ 저장
--model lstm: LSTMSignalGenerator.train(), passed 시 저장
"""

import argparse
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("train_ml")


def parse_args():
    p = argparse.ArgumentParser(description="ML model training script")
    p.add_argument("--symbol", default="BTC/USDT")
    p.add_argument("--timeframe", default="1h")
    p.add_argument("--model", choices=["rf", "lstm"], default="rf")
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--demo", action="store_true", help="MockExchangeConnector 사용")
    return p.parse_args()


def get_connector(symbol: str, demo: bool):
    if demo:
        from src.exchange.mock_connector import MockExchangeConnector
        conn = MockExchangeConnector(symbol=symbol)
    else:
        from src.exchange.connector import ExchangeConnector
        import os
        conn = ExchangeConnector(
            exchange_name=os.getenv("EXCHANGE", "binance"),
            sandbox=True,
        )
    conn.connect()
    return conn


def fetch_df(connector, symbol: str, timeframe: str, limit: int):
    from src.data.feed import DataFeed
    feed = DataFeed(connector)
    summary = feed.fetch(symbol, timeframe, limit=limit)
    logger.info("Fetched %d candles (%s ~ %s)", summary.candles, summary.start, summary.end)
    return summary.df


def train_rf(df, symbol: str):
    from src.ml.trainer import WalkForwardTrainer
    trainer = WalkForwardTrainer(symbol=symbol)
    result = trainer.train(df)
    print(result.summary())
    if result.passed:
        path = trainer.save()
        print(f"Model saved: {path}")
    else:
        print("Training FAILED — model not saved")
    return result


def train_lstm(df, symbol: str):
    from src.ml.lstm_model import LSTMSignalGenerator
    gen = LSTMSignalGenerator(symbol=symbol)
    result = gen.train(df)

    passed = result.get("passed", False)
    test_acc = result.get("test_accuracy", 0.0)
    model_path = result.get("model_path")
    fail_reasons = result.get("fail_reasons", [])

    print("ML_TRAINING_RESULT:")
    print(f"  model: lstm_{symbol.replace('/', '').lower()}")
    print(f"  test_accuracy: {test_acc:.4f}")
    print(f"  verdict: {'PASS' if passed else 'FAIL'}")
    if fail_reasons:
        print(f"  fail_reasons: {fail_reasons}")
    if model_path:
        print(f"  saved: {model_path}")

    return result


def main():
    args = parse_args()
    logger.info("train_ml.py: symbol=%s timeframe=%s model=%s limit=%d demo=%s",
                args.symbol, args.timeframe, args.model, args.limit, args.demo)

    connector = get_connector(args.symbol, args.demo)
    df = fetch_df(connector, args.symbol, args.timeframe, args.limit)

    if args.model == "rf":
        train_rf(df, args.symbol)
    else:
        train_lstm(df, args.symbol)


if __name__ == "__main__":
    main()
