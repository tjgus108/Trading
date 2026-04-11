"""Shared test fixtures for strategy unit tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    """
    기본 샘플 DataFrame 생성.
    open, high, low, close, volume 필드 포함.
    100~110 범위의 가격, 1000의 거래량.
    """
    n = 100
    close = np.linspace(100.0, 110.0, n)
    high = close + np.abs(np.random.randn(n) * 1.0)
    low = close - np.abs(np.random.randn(n) * 1.0)
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    })
    return df


@pytest.fixture
def sample_df_with_ema(sample_df):
    """
    EMA 지표를 포함한 DataFrame.
    ema20, ema50 칼럼 추가.
    """
    df = sample_df.copy()
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def _make_df(n: int = 100, close_prices=None) -> pd.DataFrame:
    """
    Internal helper for backward compatibility with existing tests.
    지표가 포함된 더미 DataFrame 생성.
    """
    if close_prices is not None:
        close = np.array(close_prices, dtype=float)
        n = len(close)
    else:
        close = np.linspace(100.0, 110.0, n)
    
    high = close + np.abs(np.random.randn(n) * 1.0)
    low = close - np.abs(np.random.randn(n) * 1.0)
    
    df = pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    })
    
    # 기본 지표 추가
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    
    # ATR14
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    
    # RSI14
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    
    # Donchian
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    
    # VWAP
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    
    return df
