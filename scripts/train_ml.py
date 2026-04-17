#!/usr/bin/env python3
"""
standalone ML training script.

usage:
  python scripts/train_ml.py [--symbol BTC/USDT] [--timeframe 1h] [--model rf|lstm] [--limit 1000] [--demo]
  python scripts/train_ml.py --auto-retrain [--symbol BTC/USDT] [--timeframe 1h]
  python scripts/train_ml.py --predict --model-file models/BTC_USDT_*.pkl [--symbol BTC/USDT]

--demo:          MockExchangeConnector 사용 (API 키 불필요)
--model rf:      WalkForwardTrainer (RandomForest), models/ 저장
--model lstm:    LSTMSignalGenerator.train(), passed 시 저장
--auto-retrain:  최근 1000캔들 Bybit fetch → binary RF 학습 → PASS 시 저장
--predict:       저장된 모델 로드 → 현재 데이터 예측
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("train_ml")

MODELS_DIR = Path(__file__).parent.parent / "models"
RETRAIN_LOG = MODELS_DIR / "retrain_log.json"
AUTO_RETRAIN_LIMIT = 1000
AUTO_RETRAIN_BINARY_THRESHOLD = 0.01
AUTO_RETRAIN_MIN_ACC = 0.55


def parse_args():
    p = argparse.ArgumentParser(description="ML model training script")
    p.add_argument("--symbol", default="BTC/USDT")
    p.add_argument("--timeframe", default="1h")
    p.add_argument("--model", choices=["rf", "lstm"], default="rf")
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--demo", action="store_true", help="MockExchangeConnector 사용")
    p.add_argument("--bybit", action="store_true", help="ccxt Bybit 직접 fetch (API 키 불필요)")
    p.add_argument("--binary", action="store_true", help="2-class (UP/DOWN) 모드, HOLD 제거")
    p.add_argument("--auto-retrain", action="store_true",
                   help="자동 재학습: 최근 1000캔들 Bybit fetch → binary RF → PASS 시 저장")
    p.add_argument("--predict", action="store_true",
                   help="예측 모드: 저장된 모델 로드 → 현재 데이터 예측")
    p.add_argument("--model-file", default=None,
                   help="--predict 시 사용할 pkl 경로 (생략 시 최신 자동 선택)")
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


def train_rf(df, symbol: str, binary: bool = False):
    from src.ml.trainer import WalkForwardTrainer
    trainer = WalkForwardTrainer(symbol=symbol, binary=binary)
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


def fetch_bybit(symbol: str, timeframe: str, limit: int):
    """ccxt Bybit에서 직접 fetch (API 키 불필요). 과거 방향 페이지네이션."""
    import ccxt
    import pandas as pd
    import time as _time

    tf_ms = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
    interval_ms = tf_ms.get(timeframe, 3_600_000)

    ex = ccxt.bybit()
    ex.timeout = 30000
    now_ms = int(_time.time() * 1000)
    since = now_ms - limit * interval_ms
    all_ohlcv = []
    stall = 0
    while len(all_ohlcv) < limit and since < now_ms:
        batch = ex.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not batch:
            stall += 1
            if stall >= 3:
                break
            since += 1000 * interval_ms
            continue
        stall = 0
        all_ohlcv.extend(batch)
        since = batch[-1][0] + interval_ms
        _time.sleep(0.3)
    seen = set()
    deduped = []
    for row in all_ohlcv:
        if row[0] not in seen:
            seen.add(row[0])
            deduped.append(row)
    deduped.sort(key=lambda x: x[0])
    deduped = deduped[:limit]
    df = pd.DataFrame(deduped, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp").sort_index()
    logger.info("Bybit: fetched %d candles (%s ~ %s)", len(df), df.index[0], df.index[-1])
    return df


def auto_retrain(symbol: str, timeframe: str):
    """
    자동 재학습 모드:
    - Bybit에서 최근 1000캔들 다운로드
    - binary=True, binary_threshold=0.01 고정
    - PASS 기준: test acc >= 55%, val acc >= 55%
    - PASS 시 models/{symbol}_{timestamp}_rf_binary.pkl 저장
    - 결과를 models/retrain_log.json에 기록
    """
    logger.info("Auto-retrain: symbol=%s timeframe=%s limit=%d", symbol, timeframe, AUTO_RETRAIN_LIMIT)
    MODELS_DIR.mkdir(exist_ok=True)

    df = fetch_bybit(symbol, timeframe, AUTO_RETRAIN_LIMIT)

    from src.ml.trainer import WalkForwardTrainer
    trainer = WalkForwardTrainer(
        symbol=symbol,
        binary=True,
    )
    result = trainer.train(df)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_symbol = symbol.replace("/", "_")

    log_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "timeframe": timeframe,
        "limit": AUTO_RETRAIN_LIMIT,
        "binary": True,
        "binary_threshold": AUTO_RETRAIN_BINARY_THRESHOLD,
        "n_samples": result.n_samples,
        "train_accuracy": result.train_accuracy,
        "val_accuracy": result.val_accuracy,
        "test_accuracy": result.test_accuracy,
        "passed": result.passed,
        "fail_reasons": result.fail_reasons,
        "model_path": None,
    }

    print(result.summary())

    if result.passed:
        model_path = str(MODELS_DIR / f"{safe_symbol}_{timestamp}_rf_binary.pkl")
        trainer.save(model_path)
        log_entry["model_path"] = model_path
        print(f"Auto-retrain PASS — saved: {model_path}")
    else:
        print("Auto-retrain FAIL — model not saved")

    # retrain_log.json 업데이트
    existing_log = []
    if RETRAIN_LOG.exists():
        try:
            with open(RETRAIN_LOG) as f:
                existing_log = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing_log = []
    existing_log.append(log_entry)
    with open(RETRAIN_LOG, "w") as f:
        json.dump(existing_log, f, indent=2)
    logger.info("Retrain log updated: %s", RETRAIN_LOG)

    return result


def predict_mode(symbol: str, timeframe: str, model_file: Optional[str], bybit: bool, demo: bool, limit: int):
    """
    예측 모드:
    - 저장된 모델 로드 (model_file 없으면 models/ 에서 최신 자동 선택)
    - 현재 데이터 fetch → predict → ML_SIGNAL 출력
    """
    from src.ml.model import MLSignalGenerator

    gen = MLSignalGenerator()

    if model_file:
        loaded = gen.load(model_file)
    else:
        loaded = gen.load_latest()

    if not loaded:
        print("ML_SIGNAL:")
        print("  action: HOLD")
        print("  confidence: 0.0")
        print("  note: no model trained")
        return

    if bybit:
        df = fetch_bybit(symbol, timeframe, limit)
    else:
        connector = get_connector(symbol, demo)
        df = fetch_df(connector, symbol, timeframe, limit)

    pred = gen.predict(df)
    print(pred.summary())


def main():
    args = parse_args()

    if args.auto_retrain:
        auto_retrain(args.symbol, args.timeframe)
        return

    if args.predict:
        predict_mode(
            symbol=args.symbol,
            timeframe=args.timeframe,
            model_file=args.model_file,
            bybit=args.bybit,
            demo=args.demo,
            limit=args.limit,
        )
        return

    logger.info("train_ml.py: symbol=%s timeframe=%s model=%s limit=%d",
                args.symbol, args.timeframe, args.model, args.limit)

    if args.bybit:
        df = fetch_bybit(args.symbol, args.timeframe, args.limit)
    else:
        connector = get_connector(args.symbol, args.demo)
        df = fetch_df(connector, args.symbol, args.timeframe, args.limit)

    if args.model == "rf":
        train_rf(df, args.symbol, binary=args.binary)
    else:
        train_lstm(df, args.symbol)


if __name__ == "__main__":
    main()
