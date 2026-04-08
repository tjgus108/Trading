"""전략 신호 생성 단위 테스트. 거래소 연결 없이 동작한다."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.base import Action
from src.strategy.donchian_breakout import DonchianBreakoutStrategy
from src.strategy.ema_cross import EmaCrossStrategy


def _make_df(n: int = 100) -> pd.DataFrame:
    """지표가 포함된 더미 DataFrame 생성."""
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    close = 50000 + np.cumsum(np.random.randn(n) * 200)
    high = close + np.abs(np.random.randn(n) * 100)
    low = close - np.abs(np.random.randn(n) * 100)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat([(df["high"] - df["low"]), (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


def test_ema_cross_returns_signal():
    df = _make_df(100)
    strategy = EmaCrossStrategy()
    signal = strategy.generate(df)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.strategy == "ema_cross"
    assert signal.entry_price > 0


def test_donchian_returns_signal():
    df = _make_df(100)
    strategy = DonchianBreakoutStrategy()
    signal = strategy.generate(df)
    assert signal.action in (Action.BUY, Action.SELL, Action.HOLD)
    assert signal.strategy == "donchian_breakout"


def test_signal_has_bull_bear_case():
    df = _make_df(100)
    signal = EmaCrossStrategy().generate(df)
    assert signal.bull_case != "" or signal.action == Action.HOLD
    assert isinstance(signal.reasoning, str)
    assert isinstance(signal.invalidation, str)


def test_ema_cross_buy_on_crossover():
    """EMA20이 EMA50을 상향 돌파하는 시나리오를 직접 주입 (ATR/VWAP 필터 포함)."""
    df = _make_df(100)
    # 마지막 두 캔들에 크로스오버 주입
    df.iloc[-3, df.columns.get_loc("ema20")] = 49000
    df.iloc[-3, df.columns.get_loc("ema50")] = 49100  # ema20 < ema50
    df.iloc[-2, df.columns.get_loc("ema20")] = 49200
    df.iloc[-2, df.columns.get_loc("ema50")] = 49100  # ema20 > ema50
    df.iloc[-2, df.columns.get_loc("rsi14")] = 55     # 과매수 아님
    # ATR 필터: 충분한 변동성 주입 (평균 atr 수준으로 설정)
    avg_atr = df["atr14"].iloc[-21:-1].mean()
    df.iloc[-2, df.columns.get_loc("atr14")] = avg_atr * 1.0  # >= 0.8 * avg_atr
    # VWAP 필터: close > vwap (BUY 조건)
    close_val = df.iloc[-2]["close"]
    df.iloc[-2, df.columns.get_loc("vwap")] = close_val * 0.99  # close > vwap
    signal = EmaCrossStrategy().generate(df)
    assert signal.action == Action.BUY
