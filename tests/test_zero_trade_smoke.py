"""
Smoke test: pair_trading, ml_rf, ml_lstm 전략이 1000캔들 백테스트에서
최소 15개 이상 거래를 생성하는지 검증.

이전 버그: 세 전략 모두 Sharpe=0.000, zero-trade 상태.
수정 후: heuristic fallback이 실제 신호를 생성해야 함.
"""

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine
from src.ml.model import MLSignalGenerator
from src.strategy.pair_trading import PairTradingStrategy
from src.strategy.ml_strategy import MLRFStrategy
from src.strategy.lstm_strategy import MLLSTMStrategy


MIN_TRADES = 15
N_CANDLES = 1000


def _make_ohlcv(n: int = N_CANDLES, seed: int = 42, trend: str = "mixed") -> pd.DataFrame:
    """백테스트용 OHLCV + 지표 DataFrame 생성."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")

    if trend == "up":
        drift = 0.0003
    elif trend == "down":
        drift = -0.0003
    else:
        # mixed: 500 up / 500 down
        drift = np.concatenate([np.full(n // 2, 0.0003), np.full(n - n // 2, -0.0003)])

    noise = rng.standard_normal(n) * 0.015
    if isinstance(drift, float):
        log_ret = drift + noise
    else:
        log_ret = drift + noise

    log_price = np.cumsum(log_ret)
    close = 50000 * np.exp(log_price)
    close = np.maximum(close, 100)

    high = close * (1 + np.abs(rng.standard_normal(n)) * 0.005)
    low = close * (1 - np.abs(rng.standard_normal(n)) * 0.005)
    low = np.minimum(low, close)
    volume = 10.0 + np.abs(rng.standard_normal(n)) * 2

    df = pd.DataFrame(
        {"open": close, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )

    # 지표 계산
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()

    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()

    return df.dropna()


class TestZeroTradeSmokeTest:
    """세 전략이 1000캔들에서 최소 15거래 생성하는지 검증."""

    def test_pair_trading_min_trades(self):
        """PairTradingStrategy: 모델/ETH 없어도 RSI fallback으로 거래 생성."""
        df = _make_ohlcv(N_CANDLES, seed=1)
        strategy = PairTradingStrategy()
        engine = BacktestEngine(initial_balance=10_000, timeframe="1h")
        result = engine.run(strategy, df)
        assert result.total_trades >= MIN_TRADES, (
            f"pair_trading: {result.total_trades} trades < {MIN_TRADES}. "
            f"Fail reasons: {result.fail_reasons}"
        )

    def test_ml_rf_min_trades(self):
        """MLRFStrategy: 모델 없어도 EMA+RSI heuristic으로 거래 생성."""
        df = _make_ohlcv(N_CANDLES, seed=2)
        with patch.object(MLSignalGenerator, "load_latest", return_value=False):
            strategy = MLRFStrategy()
        assert strategy._generator._model is None, "테스트 환경에 모델 파일이 있어서는 안 됨"
        engine = BacktestEngine(initial_balance=10_000, timeframe="1h")
        result = engine.run(strategy, df)
        assert result.total_trades >= MIN_TRADES, (
            f"ml_rf: {result.total_trades} trades < {MIN_TRADES}. "
            f"Fail reasons: {result.fail_reasons}"
        )

    def test_ml_lstm_min_trades(self):
        """MLLSTMStrategy: 모델 없어도 momentum+RSI heuristic으로 거래 생성."""
        df = _make_ohlcv(N_CANDLES, seed=3)
        strategy = MLLSTMStrategy()
        assert strategy._generator._model is None, "테스트 환경에 모델 파일이 있어서는 안 됨"
        engine = BacktestEngine(initial_balance=10_000, timeframe="1h")
        result = engine.run(strategy, df)
        assert result.total_trades >= MIN_TRADES, (
            f"ml_lstm: {result.total_trades} trades < {MIN_TRADES}. "
            f"Fail reasons: {result.fail_reasons}"
        )

    def test_all_three_strategies_generate_trades_mixed_trend(self):
        """세 전략 모두 mixed 추세 데이터에서 거래 생성."""
        df = _make_ohlcv(N_CANDLES, seed=99, trend="mixed")
        engine = BacktestEngine(initial_balance=10_000, timeframe="1h")

        strategies = [
            PairTradingStrategy(),
            MLRFStrategy(),
            MLLSTMStrategy(),
        ]

        for strategy in strategies:
            result = engine.run(strategy, df)
            assert result.total_trades >= MIN_TRADES, (
                f"{strategy.name}: only {result.total_trades} trades on mixed trend. "
                f"Still zero-trade bug?"
            )
